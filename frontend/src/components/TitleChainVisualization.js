import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';

const TitleChainVisualization = ({ titleChain }) => {
  const svgRef = useRef(null);
  const containerRef = useRef(null);
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [dims, setDims] = useState({ width: 800, height: 320 });

  useEffect(() => {
    if (containerRef.current) {
      const w = containerRef.current.getBoundingClientRect().width;
      setDims({ width: w, height: 320 });
    }
  }, []);

  useEffect(() => {
    if (!svgRef.current || !titleChain?.chain?.length) return;
    renderChart();
  }, [titleChain, dims]);

  const renderChart = () => {
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const { width, height } = dims;
    const chain = titleChain.chain;
    const pad = { top: 40, right: 40, bottom: 60, left: 40 };
    const usable = width - pad.left - pad.right;
    const nodeW = Math.min(140, usable / chain.length - 20);
    const nodeH = 60;
    const spacing = usable / Math.max(chain.length - 1, 1);

    const g = svg.append('g').attr('transform', `translate(${pad.left},${pad.top})`);
    const centerY = (height - pad.top - pad.bottom) / 2;

    // Timeline line
    g.append('line')
      .attr('x1', 0).attr('y1', centerY)
      .attr('x2', usable).attr('y2', centerY)
      .attr('stroke', '#334155').attr('stroke-width', 2)
      .attr('stroke-dasharray', '6,4');

    // Connections between nodes
    chain.forEach((entry, i) => {
      if (i < chain.length - 1) {
        const x1 = i * spacing + nodeW / 2;
        const x2 = (i + 1) * spacing - nodeW / 2;
        const hasGap = titleChain.gaps?.some(g =>
          g.between?.includes(entry.owner_name) || g.between?.includes(chain[i + 1]?.owner_name)
        );

        g.append('line')
          .attr('x1', x1 + nodeW / 2).attr('y1', centerY)
          .attr('x2', x2 + nodeW / 2).attr('y2', centerY)
          .attr('stroke', hasGap ? '#f59e0b' : '#06b6d4')
          .attr('stroke-width', hasGap ? 3 : 2)
          .attr('stroke-dasharray', hasGap ? '8,4' : 'none')
          .attr('opacity', 0)
          .transition().delay(i * 200 + 100).duration(400)
          .attr('opacity', 0.8);

        // Arrow
        const midX = (x1 + nodeW / 2 + x2 + nodeW / 2) / 2;
        g.append('polygon')
          .attr('points', `${midX - 5},${centerY - 5} ${midX + 5},${centerY} ${midX - 5},${centerY + 5}`)
          .attr('fill', hasGap ? '#f59e0b' : '#06b6d4')
          .attr('opacity', 0)
          .transition().delay(i * 200 + 200).duration(300)
          .attr('opacity', 0.8);

        // Transfer label
        g.append('text')
          .attr('x', midX).attr('y', centerY - 12)
          .attr('text-anchor', 'middle')
          .attr('font-size', '9px')
          .attr('fill', '#64748b')
          .text(chain[i + 1]?.transfer_type || '')
          .attr('opacity', 0)
          .transition().delay(i * 200 + 250).duration(300)
          .attr('opacity', 1);
      }
    });

    // Nodes
    const nodes = g.selectAll('.node')
      .data(chain).enter().append('g')
      .attr('class', 'node')
      .attr('transform', (d, i) => `translate(${i * spacing},${centerY - nodeH / 2})`)
      .attr('cursor', 'pointer')
      .on('click', (event, d) => setSelectedEntry(d));

    // Node animation
    nodes.attr('opacity', 0)
      .transition().delay((d, i) => i * 200).duration(400)
      .attr('opacity', 1);

    // Node background
    nodes.append('rect')
      .attr('width', nodeW).attr('height', nodeH)
      .attr('rx', 8).attr('ry', 8)
      .attr('fill', (d, i) => i === 0 ? 'rgba(6, 182, 212, 0.15)' : 'rgba(99, 102, 241, 0.12)')
      .attr('stroke', (d, i) => i === 0 ? '#06b6d4' : d.verified ? '#10b981' : '#f59e0b')
      .attr('stroke-width', 1.5);

    // Owner name
    nodes.append('text')
      .attr('x', nodeW / 2).attr('y', nodeH / 2 - 6)
      .attr('text-anchor', 'middle')
      .attr('font-size', '11px')
      .attr('font-weight', '600')
      .attr('fill', '#e2e8f0')
      .text(d => d.owner_name?.length > 16 ? d.owner_name.slice(0, 14) + '..' : d.owner_name);

    // Date
    nodes.append('text')
      .attr('x', nodeW / 2).attr('y', nodeH / 2 + 12)
      .attr('text-anchor', 'middle')
      .attr('font-size', '9px')
      .attr('fill', '#64748b')
      .text(d => d.transfer_date);

    // Verification status icon
    nodes.append('circle')
      .attr('cx', nodeW - 8).attr('cy', 8).attr('r', 5)
      .attr('fill', d => d.verified ? '#10b981' : '#f59e0b');

    // Year labels at bottom
    chain.forEach((entry, i) => {
      const year = entry.transfer_date?.split('-')[0] || '';
      g.append('text')
        .attr('x', i * spacing + nodeW / 2)
        .attr('y', centerY + nodeH / 2 + 25)
        .attr('text-anchor', 'middle')
        .attr('font-size', '10px')
        .attr('fill', '#94a3b8')
        .attr('font-weight', '500')
        .text(year);
    });

    // Title
    svg.append('text')
      .attr('x', pad.left).attr('y', 20)
      .attr('font-size', '12px')
      .attr('fill', '#94a3b8')
      .text(`Ownership Timeline (${titleChain.chain_span_years}+ years)`);
  };

  return (
    <div ref={containerRef} data-testid="title-chain-d3-viz">
      <div className="bg-slate-900/50 rounded-lg border border-slate-700/50 overflow-hidden">
        <svg ref={svgRef} width={dims.width} height={dims.height} style={{ display: 'block' }} data-testid="title-chain-svg" />
      </div>

      {selectedEntry && (
        <div className="mt-4 p-4 bg-slate-800/80 rounded-lg border border-slate-700/50" data-testid="title-chain-detail">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-semibold text-white">{selectedEntry.owner_name}</h4>
            <button onClick={() => setSelectedEntry(null)} className="text-xs text-slate-500 hover:text-white">Close</button>
          </div>
          <div className="grid grid-cols-2 gap-3 text-xs">
            {[
              ['Transfer Type', selectedEntry.transfer_type],
              ['Date', selectedEntry.transfer_date],
              ['Document', selectedEntry.doc_ref],
              ['Extent', selectedEntry.extent],
              ['Consideration', selectedEntry.consideration],
              ['Registrar', selectedEntry.registrar],
              ['Father Name', selectedEntry.father_name],
              ['Verified', selectedEntry.verified ? 'Yes' : 'Pending'],
            ].filter(([, v]) => v && v !== 'N/A').map(([k, v]) => (
              <div key={k}>
                <span className="text-slate-500">{k}: </span>
                <span className="text-slate-300">{v}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TitleChainVisualization;
