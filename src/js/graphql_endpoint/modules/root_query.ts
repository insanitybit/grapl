import {printSchema} from "graphql/utilities";
import {
    GraphQLObjectType,
    GraphQLInt,
    GraphQLString,
    GraphQLList,
    GraphQLSchema,
    GraphQLNonNull,
} from "graphql";

import { BaseNode, builtins } from "./schema";

import {
    getDgraphClient,
    DgraphClient,
    RawNode,
    EnrichedNode,
} from "./dgraph_client";
import { SchemaClient } from "./schema_client";
import { allSchemasToGraphql } from "./schema_to_graphql";

type MysteryParentType = never;

const getLenses = async (
    dg_client: DgraphClient,
    first: number,
    offset: number
) => {
    console.debug("first, offset parameters in getLenses()", first, offset);

    const query = `
        query all($a: int, $b: int)
        {
            all(func: type(Lens), first: $a, offset: $b, orderdesc: score)
            {
                lens_name,
                score,
                node_key,
                uid,
                dgraph_type: dgraph.type,
                lens_type,
                scope {
                    uid,
                    node_key,
                    dgraph_type: dgraph.type,
                }
            }
        }
    `;

    console.debug("Creating DGraph txn in getLenses");

    const txn = dg_client.newTxn();

    try {
        console.debug("Querying DGraph for lenses in getLenses");
        const res = await txn.queryWithVars(query, {
            $a: first.toString(),
            $b: offset.toString(),
        });
        console.debug("Lens response from DGraph", res);
        return res.getJson()["all"];
    } catch (e) {
        console.error("Error in DGraph txn getLenses: ", e);
    } finally {
        console.debug("Closing Dgraph Txn in getLenses");
        await txn.discard();
    }
};

interface LensSubgraph {
    readonly node_key: string;
    readonly lens_name: string;
    readonly lens_type: string;
    readonly score: number;
    scope: RawNode[];
}

const getLensSubgraphByName = async (
    dg_client: DgraphClient,
    lens_name: string
) => {
    const query = `
        query all($a: string, $b: first, $c: offset) {
            all(func: eq(lens_name, $a), first: 1) {
                uid,
                dgraph_type: dgraph.type,
                node_key,
                lens_name,
                lens_type,
                score,
                scope @filter(has(node_key)) {
                    uid,
                    dgraph_type: dgraph.type,
                    expand(_all_) {
                        uid,
                        dgraph_type: dgraph.type,
                        expand(_all_)
                    }
                }
            }
        }
    `;

    console.debug("Creating DGraph txn in getLensSubgraphByName");
    const txn = dg_client.newTxn();

    try {
        console.debug("Querying DGraph in getLensSubgraphByName");
        const res = await txn.queryWithVars(query, { $a: lens_name });
        console.debug(
            "returning following data from getLensSubGrapByName: ",
            res.getJson()["all"][0]
        );
        return res.getJson()["all"][0] as LensSubgraph & RawNode;
    } catch (e) {
        console.error("Error in DGraph txn: getLensSubgraphByName", e);
    } finally {
        console.debug("Closing dgraphtxn in getLensSubraphByName");
        await txn.discard();
    }
};

const filterDefaultDgraphNodeTypes = (node_type: string) => {
    return node_type !== "Base" && node_type !== "Entity";
};

function hasDgraphType(node: RawNode): boolean {
    return "dgraph_type" in node && !!node["dgraph_type"];
}

function uidAsInt(node: RawNode): number {
    const uid = node["uid"];

    if (typeof uid == "string") {
        return parseInt(uid, 16);
    } else if (typeof uid == "number") {
        return uid;
    }
    throw new Error(`Oddly typed UID ${uid}`);
}

function asEnrichedNode(node: RawNode): EnrichedNode {
    return {
        ...node,
        uid: uidAsInt(node),
        dgraph_type: node.dgraph_type?.filter(filterDefaultDgraphNodeTypes),
    };
}

const handleLensScope = async (parent: MysteryParentType, args: LensArgs) => {
  console.debug("handleLensScope args: ", args);
  const dg_client = getDgraphClient();

  const lens_name = args.lens_name;

  // grab the graph of lens, lens scope, and neighbors to nodes in-scope of the lens ((lens) -> (neighbor) -> (neighbor's neighbor))
  const lens_subgraph: (LensSubgraph & RawNode) = await getLensSubgraphByName(dg_client, lens_name);
  console.debug("lens_subgraph in handleLensScope: ", lens_subgraph);

  lens_subgraph.uid = uidAsInt(lens_subgraph);
  let scope: EnrichedNode[] = (lens_subgraph["scope"] || []).map(asEnrichedNode);

  // No dgraph_type? Not a node; skip it!
  scope = scope.filter(
    (neighbor: EnrichedNode) => neighbor.dgraph_type.length > 0
  );

  // record the uids of all direct neighbors to the lens.
  // These are the only nodes we should keep by the end of this process.
  // We'll then try to get all neighbor connections that only correspond to these nodes
  const neighbor_uids = new Set<number>(
    scope.map((node: EnrichedNode) => node["uid"])
  );

  // lens neighbors
  for (const neighbor of scope) {
    // neighbor of a lens neighbor
    for (const predicate in neighbor) {
      // we want to keep risks and enrich them at the same time
      if (predicate === "risks") {
        const risks = neighbor[predicate].map(asEnrichedNode);
        risks.forEach((risk_node: EnrichedNode) => {
          if (hasDgraphType(risk_node)) {
            console.debug("checking if dgraph_type in risk_node", risk_node);
            risk_node["dgraph_type"] = risk_node["dgraph_type"].filter(
              filterDefaultDgraphNodeTypes
            );
          }
        });

        // filter out nodes that don't have dgraph_types
        neighbor[predicate] = risks.filter(hasDgraphType);
        continue;
      }

      // If this edge is 1-to-many, we need to filter down the list to lens-neighbor -> lens-neighbor connections
      if (
        Array.isArray(neighbor[predicate]) &&
        neighbor[predicate] &&
        neighbor[predicate][0]["uid"]
      ) {
        neighbor[predicate] = neighbor[predicate].map(asEnrichedNode);
        neighbor[predicate] = neighbor[
          predicate
        ].filter((second_neighbor: EnrichedNode) =>
          neighbor_uids.has(second_neighbor["uid"])
        );

        // If we filtered all the edges down, might as well delete this predicate
        if (neighbor[predicate].length === 0) {
          delete neighbor[predicate];
        }
      }
      // If this edge is 1-to-1, we need to determine if we need to delete the edge
      else if (
        typeof neighbor[predicate] === "object" &&
        neighbor[predicate]["uid"]
      ) {
        const enriched = asEnrichedNode(neighbor[predicate]);
        if (!neighbor_uids.has(enriched.uid)) {
          delete neighbor[predicate];
        } else {
          neighbor[predicate] = enriched;
        }

		// TODO improve this display stuff
        for (const node of scope) {
            const _node = node as any;
            const nodeType = _node.dgraph_type.filter(
                filterDefaultDgraphNodeTypes
            )[0];
            console.log("nodeType", nodeType)
            const displayProperty = await getDisplayProperty(nodeType);

            if (_node[displayProperty.S] === undefined) {
                _node["display"] = nodeType;
            } else {
                _node["display"] = _node[displayProperty.S].toString();
            }
        }
      }
    }
  }

  for (const node of scope) {
    if (!node) {
      throw new Error(`Somehow received a null or undefined scope node: ${node}`);
    }
  }

  lens_subgraph.scope = scope;
  console.debug("lens_subgraph scope", JSON.stringify(lens_subgraph["scope"]));
  return lens_subgraph;
};

interface RootQueryArgs {
    readonly first: number;
    readonly offset: number;
}

interface LensArgs {
    readonly lens_name: string;
}

async function getRootQuery(): Promise<GraphQLObjectType> {
  const types = await new SchemaClient().getSchemas();
  const typesWithoutBuiltins = types.filter((schema) => {
    // This could be a one-liner, but I think it's complex enough for ifelse
    console.log("HEYYY");
    console.log(schema.node_type);
    if (schema.node_type == "Risk" || schema.node_type == "Lens") {
      console.log("YABBA DABBA DOO");
      return false; // reject
    } else {
      return true; // keep
    }
  });
  const GraplEntityType = allSchemasToGraphql(typesWithoutBuiltins);
  const LensNodeType = new GraphQLObjectType({
    name: "LensNode",
    fields: () => ({
      ...BaseNode,
      lens_name: { type: GraphQLString },
      score: { type: GraphQLInt },
      scope: { type: GraphQLList(GraplEntityType) },
      lens_type: { type: GraphQLString },
    }),
  });

  return new GraphQLObjectType({
    name: "RootQueryType",
    fields: {
      lenses: {
        type: GraphQLList(LensNodeType),
        args: {
          first: {
            type: new GraphQLNonNull(GraphQLInt),
          },
          offset: {
            type: new GraphQLNonNull(GraphQLInt),
          },
        },
        resolve: async (parent: MysteryParentType, args: RootQueryArgs) => {
          console.debug("lenses query arguments", args);
          const first = args.first;
          const offset = args.offset;
          // #TODO: Make sure to validate that 'first' is under a specific limit, maybe 1000
          console.debug("Making getLensesQuery");
          const lenses = await getLenses(getDgraphClient(), first, offset);
          console.debug(
            "returning data from getLenses for lenses resolver",
            lenses
          );
          return lenses;
        },
      },
      lens_scope: {
        type: LensNodeType,
        args: {
          lens_name: { type: new GraphQLNonNull(GraphQLString) },
        },
        resolve: async (parent: MysteryParentType, args: LensArgs) => {
          try {
            console.debug("lens_scope args: ", args);
            let response = await handleLensScope(parent, args);
            console.debug("lens_scope response: ", response);
            return response;
          } catch (e) {
            console.error("Error in handleLensScope: ", e);
            throw e;
          }
        },
      },
    },
  });
}

export async function getRootQuerySchema(): Promise<GraphQLSchema> {
  const schema = new GraphQLSchema({
    query: await getRootQuery(),
  });
  console.log("Schema: ", printSchema(schema));
  return schema;
}
