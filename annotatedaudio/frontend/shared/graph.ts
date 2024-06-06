export default class Graph {
    edges: Map<string, string[]>;
    numNodes: number = 0;

    constructor(){
        this.edges = new Map<string, string[]>();
    }

    /**
     * Get the number of node in this graph
     * @returns number of node in this graph
     */
    public getNumNodes(): number {
        return this.numNodes;
    }
    
    /**
     * Get the list of nodes in this graph
     * @returns list of nodes
     */
    public getNodesList(): string[] {
        return Array.from(this.edges.keys());
    }

    /**
     * Get nodes adjacent to the specified one
     * @param node
     * @returns adjacent nodes in this graph
     */
    public getAdjNodes(node: string): string[] | undefined{
        return this.edges.get(node);
    }

    /**
     *  Check whether the specified node is in this graph
     * @param node node to be be checked
     * @returns true if the specified node is in this graph, false otherwise
     */
    public isNodeInGraph(node: string) {
        return this.edges.get(node) !== undefined;
    }

    /**
     * Check whether the edge (node1, node2) is in this graph. Calling this method for
     * the edge (node2, node1) will return the same result, as the graph is non-oriented.
     * @param node1 edge's first node
     * @param node2 edge's second node
     * @returns true if the edge is in this graph, false otherwise
     */
    public isEdgeInGraph(node1: string, node2: string){
        let adjNodes = this.getAdjNodes(node1);
        if(adjNodes === undefined){
            return false;
        }
        if(adjNodes.find(adjNode => adjNode == node2) === undefined){
            return false;
        }
        return true;
    }

    /**
     * Add specified node to this graph
     * @param node node to be added
     */
    public addNode(node: string): void{
        if(!this.isNodeInGraph(node)){
            this.edges.set(node, []);
            this.numNodes += 1;
        }
    }

    /**
     * Add an edge between the two specified node
     * Note: (node1, node2) === (node2, node1)
     * @param node1 edge's first node
     * @param node2 edge's second node
     */
    public addEdge(node1:string, node2: string): void{
        // do not create an edge if nodes are the same
        if(node1 === node2){
            return;
        }

        // do not add a edge if it already exists
        if(this.isEdgeInGraph(node1, node2)){
            return;
        }

        if(!this.isNodeInGraph(node1)){
            this.addNode(node1);
        }
        if(!this.isNodeInGraph(node2)){
            this.addNode(node2);
        }
        // non-oriented graph
        this.getAdjNodes(node1)?.push(node2);
        this.getAdjNodes(node2)?.push(node1);
    }

    /**
     * Remove the specified node from this graph
     * @param node node to be removed
     * @returns true if the node has been successfully removed, false otherwise
     */
    public removeNode(node: string): boolean {
        let adjNodes = this.getAdjNodes(node);
        if(adjNodes !== undefined){
            // remove all the corresponding edges
            adjNodes.forEach(adjNode => {
                this.removeEdge(node, adjNode);
            })
            // remove node from the grap
            this.edges.delete(node);
            this.numNodes -= 1;

            return true;
        }
        return false;
    }

    /**
     * Remove the edge (node1, node2) from this graph. Calling this method for edge
     * (node2, node1) will give the same result.
     * @param node1 edge's first node
     * @param node2 edge's second node
     */
    public removeEdge(node1:string, node2: string): void{
        if(!this.isEdgeInGraph(node1, node2)){
            // if one of the specified node not in graph, do nothing
            return;
        }
        this.getAdjNodes(node1)?.splice(Number(this.getAdjNodes(node1)?.indexOf(node2)), 1);
        this.getAdjNodes(node2)?.splice(Number(this.getAdjNodes(node1)?.indexOf(node1)), 1);
    }

    /**
     * 
     * @returns 
     */
    public greedyColoring(){
        // map associating a color at each graph node:
        let nodesColor = new Map<string, number>()
        let isColorAvailable = new Array(this.numNodes).fill(true);
        
        this.getNodesList().forEach(node => {
            this.getAdjNodes(node)?.forEach(adjNode =>{
                // get color of adjacent nodes and remove them from available color
                let nodeColor = nodesColor.get(adjNode);
                if(nodeColor !== undefined){
                    isColorAvailable[nodeColor] = false;
                }
            });
            let color: number;
            for(color = 0; color < isColorAvailable.length; color++){
                if(isColorAvailable[color]) break; // available color found
            }
            nodesColor.set(node, color);
            // reset available color for the next iteration
            isColorAvailable.fill(true);
        });

        return nodesColor;
    }

    /**
     * Get the connected component of the graph to which the specified node belongs.
     * @param node 
     * @returns A graph representing the connected component of the specified node.
     */
    public getConnectedComponent(node: string): Graph {
        let visitedNodes: string[] = [];
        let connectedComponent: Graph = new Graph();

        this.getConnectedComponentHelper(node, visitedNodes, connectedComponent);
        
        return connectedComponent;
    }

    private getConnectedComponentHelper(node: string, visitedNodes: string[], connectedComponent: Graph): void{
        visitedNodes.push(node);
        connectedComponent.addNode(node);
        this.getAdjNodes(node)?.forEach(adjNode => {
            connectedComponent.addEdge(node, adjNode);
            if(visitedNodes.find(visitedNode => visitedNode === adjNode) === undefined){
                this.getConnectedComponentHelper(adjNode, visitedNodes, connectedComponent);
            }
        });
    }

}
