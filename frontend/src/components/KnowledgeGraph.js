import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';

const KnowledgeGraph = ({ propertyId, titleChain, property, documents }) => {
  const svgRef = useRef(null);
  const containerRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 500 });

  useEffect(() => {
    if (containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      setDimensions({ width: rect.width, height: 500 });
    }
  }, []);

  useEffect(() => {
    if (!svgRef.current || !property) return;
    buildGraph();
  }, [property, titleChain, documents, dimensions]);

  const buildGraph = () => {
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const { width, height } = dimensions;
    const nodes = [];
    const links = [];

    // Property node (center)
    nodes.push({
      id: propertyId,
      label: `Survey ${property?.survey_no || 'N/A'}`,
      type: 'property',
      detail: `${property?.district}, ${property?.state}`,
      radius: 32,
    });

    // Owner nodes from title chain
    const chain = titleChain?.chain || [];
    chain.forEach((entry, i) => {
      const ownerId = `owner_${i}`;
      nodes.push({
        id: ownerId,
        label: entry.owner_name,
        type: i === 0 ? 'current_owner' : 'previous_owner',
        detail: `${entry.transfer_type} (${entry.transfer_date})`,
        radius: i === 0 ? 26 : 20,
      });
      links.push({ source: propertyId, target: ownerId, label: entry.transfer_type, type: 'ownership' });
      if (i > 0) {
        links.push({ source: `owner_${i - 1}`, target: ownerId, label: 'from', type: 'transfer' });
      }
    });

    // Document nodes
    const docs = documents || [];
    docs.slice(0, 5).forEach((doc, i) => {
      const docId = `doc_${i}`;
      nodes.push({
        id: docId,
        label: doc.doc_type || doc.filename || `Doc ${i + 1}`,
        type: 'document',
        detail: doc.filename || '',
        radius: 16,
      });
      links.push({ source: propertyId, target: docId, label: 'has doc', type: 'document' });
    });

    // Location node
    nodes.push({
      id: 'location',
      label: property?.district || 'Location',
      type: 'location',
      detail: `${property?.taluk || ''}, ${property?.state || ''}`,
      radius: 22,
    });
    links.push({ source: propertyId, target: 'location', label: 'located in', type: 'location' });

    // Government node
    nodes.push({
      id: 'govt',
      label: 'Govt Records',
      type: 'government',
      detail: 'Land Revenue Dept',
      radius: 20,
    });
    links.push({ source: propertyId, target: 'govt', label: 'registered', type: 'government' });

    const colorMap = {
      property: '#06b6d4',
      current_owner: '#10b981',
      previous_owner: '#6366f1',
      document: '#f59e0b',
      location: '#ec4899',
      government: '#8b5cf6',
    };

    // Force simulation
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id(d => d.id).distance(120))
      .force('charge', d3.forceManyBody().strength(-400))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(d => d.radius + 15));

    // Zoom
    const g = svg.append('g');
    svg.call(d3.zoom().scaleExtent([0.3, 3]).on('zoom', (event) => {
      g.attr('transform', event.transform);
    }));

    // Links
    const link = g.append('g').selectAll('line')
      .data(links).join('line')
      .attr('stroke', d => d.type === 'transfer' ? '#6366f1' : '#334155')
      .attr('stroke-width', d => d.type === 'transfer' ? 2 : 1.5)
      .attr('stroke-dasharray', d => d.type === 'document' ? '4,4' : 'none')
      .attr('opacity', 0.6);

    // Link labels
    const linkLabel = g.append('g').selectAll('text')
      .data(links).join('text')
      .text(d => d.label)
      .attr('font-size', '9px')
      .attr('fill', '#64748b')
      .attr('text-anchor', 'middle');

    // Nodes
    const node = g.append('g').selectAll('g')
      .data(nodes).join('g')
      .attr('cursor', 'pointer')
      .call(d3.drag()
        .on('start', (event, d) => { if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
        .on('drag', (event, d) => { d.fx = event.x; d.fy = event.y; })
        .on('end', (event, d) => { if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; })
      )
      .on('click', (event, d) => {
        setSelectedNode(d);
      });

    // Node circles with glow
    node.append('circle')
      .attr('r', d => d.radius)
      .attr('fill', d => colorMap[d.type] || '#64748b')
      .attr('fill-opacity', 0.15)
      .attr('stroke', d => colorMap[d.type] || '#64748b')
      .attr('stroke-width', 2);

    // Node icons (text)
    node.append('text')
      .text(d => {
        const icons = { property: '\u2302', current_owner: '\u263A', previous_owner: '\u263A', document: '\u2709', location: '\u2690', government: '\u2691' };
        return icons[d.type] || '\u25CF';
      })
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'central')
      .attr('font-size', d => d.radius * 0.8)
      .attr('fill', d => colorMap[d.type] || '#64748b');

    // Node labels
    node.append('text')
      .text(d => d.label.length > 18 ? d.label.slice(0, 16) + '...' : d.label)
      .attr('y', d => d.radius + 14)
      .attr('text-anchor', 'middle')
      .attr('font-size', '11px')
      .attr('fill', '#e2e8f0')
      .attr('font-weight', '500');

    simulation.on('tick', () => {
      link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
      linkLabel.attr('x', d => (d.source.x + d.target.x) / 2)
        .attr('y', d => (d.source.y + d.target.y) / 2 - 6);
      node.attr('transform', d => `translate(${d.x},${d.y})`);
    });
  };

  return (
    <div ref={containerRef} data-testid="knowledge-graph-container">
      <div className="flex items-center justify-between mb-4">
        <div className="flex flex-wrap gap-3">
          {[
            { color: '#06b6d4', label: 'Property' },
            { color: '#10b981', label: 'Current Owner' },
            { color: '#6366f1', label: 'Previous Owners' },
            { color: '#f59e0b', label: 'Documents' },
            { color: '#ec4899', label: 'Location' },
            { color: '#8b5cf6', label: 'Government' },
          ].map(item => (
            <div key={item.label} className="flex items-center gap-1.5 text-xs text-slate-400">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color, opacity: 0.7 }} />
              {item.label}
            </div>
          ))}
        </div>
        <p className="text-xs text-slate-500">Drag nodes to explore. Scroll to zoom.</p>
      </div>

      <div className="relative bg-slate-900/50 rounded-lg border border-slate-700/50 overflow-hidden">
        <svg
          ref={svgRef}
          width={dimensions.width}
          height={dimensions.height}
          style={{ display: 'block' }}
          data-testid="knowledge-graph-svg"
        />
      </div>

      {selectedNode && (
        <div className="mt-4 p-4 bg-slate-800/80 rounded-lg border border-slate-700/50" data-testid="graph-node-detail">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-semibold text-white">{selectedNode.label}</h4>
            <button onClick={() => setSelectedNode(null)} className="text-slate-500 hover:text-white text-xs">Close</button>
          </div>
          <p className="text-xs text-slate-400">Type: <span className="text-cyan-400 capitalize">{selectedNode.type.replace('_', ' ')}</span></p>
          {selectedNode.detail && <p className="text-xs text-slate-400 mt-1">{selectedNode.detail}</p>}
        </div>
      )}
    </div>
  );
};

export default KnowledgeGraph;
