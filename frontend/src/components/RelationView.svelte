<script>
  import { onMount } from 'svelte';

  export let relation_data = null;

  // Sample data - would be replaced with API fetch
  let relationshipData = {
    matrix: {
      'a': {
        'b': 0.145,
        'c': 0.245
      },
      'b': {},
      'c': {}
    }
  };

  // Map of element IDs to their display names
  const elementLabels = {
    'a': 'PDF File 1',
    'b': 'PDF File 2',
    'c': 'PDF File 3'
  };

  // Map of element IDs to their colors
  const elementColors = {
    'a': 'bg-orange-600',
    'b': 'bg-green-500',
    'c': 'bg-purple-600'
  };

  let activeElement = null;
  let connections = [];

  // SVG path generator for curved connection lines
  function generateCurvedPath(startX, startY, endX, endY) {
    const midX = (startX + endX) / 2;
    return `M ${startX} ${startY} C ${midX} ${startY}, ${midX} ${endY}, ${endX} ${endY}`;
  }

  function showConnections(elementId) {
    console.log(relation_data);

    activeElement = elementId;
    connections = [];

    const relations = relationshipData.matrix[elementId] || {};
    for (const targetId in relations) {
      if (relations[targetId] > 0) {
        connections.push({
          source: elementId,
          target: targetId,
          weight: relations[targetId]
        });
      }
    }
  }

  function hideConnections() {
    activeElement = null;
    connections = [];
  }
</script>

<div class="bg-white p-6 rounded-lg shadow-md">
<div class="relative w-full h-full min-h-64 flex flex-col items-center">
  <!-- SVG for connection lines -->
  <svg class="absolute inset-0 w-full h-full pointer-events-none z-10">
    {#each connections as connection}
      {@const sourceElement = document.getElementById(`element-${connection.source}`)}
      {@const targetElement = document.getElementById(`element-${connection.target}-target`)}

      {#if sourceElement && targetElement}
        {@const sourceRect = sourceElement.getBoundingClientRect()}
        {@const targetRect = targetElement.getBoundingClientRect()}
        {@const containerRect = sourceElement.parentElement.getBoundingClientRect()}

        {@const sourceX = sourceRect.right - containerRect.left}
        {@const sourceY = sourceRect.top + sourceRect.height/2 - containerRect.top}
        {@const targetX = targetRect.left - containerRect.left}
        {@const targetY = targetRect.top + targetRect.height/2 - containerRect.top}

        {@const midX = (sourceX + targetX) / 2}
        {@const midY = (sourceY + targetY) / 2}

        <!-- Connection path -->
        <path
          d={generateCurvedPath(sourceX, sourceY, targetX, targetY)}
          fill="none"
          stroke="#0d6efd"
          stroke-width="2"
          class="transition-opacity duration-300"
        />

        <!-- Weight label -->
        <text
          x={midX + 5}
          y={midY - 10}
          fill="#0d6efd"
          class="text-sm font-medium"
        >
          {connection.weight}
        </text>
      {/if}
    {/each}
  </svg>

  <div class="flex justify-between w-full mb-16">
    <!-- Left column -->
    <div class="flex flex-col gap-8 pl-8 w-1/3">
      {#each Object.keys(relationshipData.matrix) as elementId}
        <div
          id={`element-${elementId}`}
          class={`rounded-full p-4 text-center text-white text-xs font-medium w-64 h-16 flex items-center justify-center cursor-pointer ${elementColors[elementId]} transition-all duration-300 hover:shadow-lg`}
          on:mouseenter={() => showConnections(elementId)}
          on:mouseleave={hideConnections}
        >
          {elementLabels[elementId]}
        </div>
      {/each}
    </div>

    <!-- Right column -->
    <div class="flex flex-col gap-8 pr-8 w-1/3">
      {#each Object.keys(relationshipData.matrix) as elementId}
        <div
          id={`element-${elementId}-target`}
          class={`rounded-full p-4 text-center text-white font-medium w-64 h-16 flex items-center justify-center ${elementColors[elementId]} ${activeElement && connections.some(c => c.target === elementId) ? 'shadow-lg' : ''}`}
        >
          {elementLabels[elementId]}
        </div>
      {/each}
    </div>
  </div>
</div>
</div>