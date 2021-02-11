import { VizGraph, VizNode } from "../../../types/CustomTypes";

export const calcNodeRiskPercentile = (
	_nodeRisk: number | { risk: number },
	_allRisks: any
) => {
	let nodeRisk = _nodeRisk;
	let riskIndex = 0;

	const allRisks = _allRisks
		.map((n: any) => n || 0)
		.sort((a: number, b: number) => a - b);

	if (typeof _nodeRisk === "object") {
		nodeRisk = _nodeRisk.risk;
	}
	if (nodeRisk === undefined || nodeRisk === 0 || allRisks.length === 0) {
		return 0;
	}	

	for (const risk of allRisks) {
		if (nodeRisk >= risk) {
			riskIndex += 1;
		}
	}
	return Math.floor((riskIndex / allRisks.length) * 100);
};

export const nodeRisk = (node: VizNode, Graph: VizGraph) => {
	const nodes = [...Graph.nodes].map((node) => node.risk);
	const _node = node as any; 
	
	const riskPercentile = calcNodeRiskPercentile(_node.risk_score, nodes);

	if (riskPercentile >= 75) {
		return 6;
	} else if (riskPercentile >= 50) {
		return 5;
	} else if (riskPercentile >= 25) {
		return 4;
	} else {
		return 3;
	}
};
