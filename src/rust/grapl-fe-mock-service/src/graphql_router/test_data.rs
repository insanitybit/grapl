use serde::{
    Serialize, Deserialize,
};

use serde_json::Value;

use std::collections::HashMap;
use serde_json::json;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Node {
    uid: u64,
    node_key: String,
    dgraph_type: Vec<String>,
    display: String,
    #[serde(flatten)]
    node_edges_and_props: HashMap<String, Value>,
}


#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Data {
    lens_scope: LensScope,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GraphQLLensScopeResp {
    data: Data,

}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LensScope {
    lens_name: String,
    nodes: Vec<Node>,
}


pub fn example_lens_scope() -> LensScope {
    let raw = json!({
        "lens_name": "ExampleLens",
        "nodes": [
            {
                "uid": 100,
                "node_key": "TestNode1",
                "dgraph_type": ["File"],
                "display": "TestFile1",
                "file_path": "src/python",
                "created_by": {
                    "uid": 200,
                    "node_key": "TestNode2",
                    "dgraph_type": ["Process"],
                    "display": "TestProcess",
                    "process_name": "evil.exe",
                }
            }
        ]
    });
    serde_json::from_value(raw).unwrap()
}


pub fn example_graphql_lens_scope_resp() -> GraphQLLensScopeResp {
    GraphQLLensScopeResp{
        data: Data{
            lens_scope: example_lens_scope()
        }
    }
}