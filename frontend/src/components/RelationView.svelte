<script>
  import { onMount } from 'svelte';
  import { createEventDispatcher } from 'svelte';

  export let relation_data = null;

  let activeElement = null;
  let connections = [];
  let elements = {};
  let fullnames = {};
  const dispatch = createEventDispatcher();

function encodePathToHtmlId(path) {
  // Handle empty input
  if (!path) {
    return 'p';
  }

  // Convert each character to a safe representation
  let encoded = '';
  for (let char of path) {
    // Check if the character is a valid ASCII character for HTML IDs
    if (/[a-zA-Z0-9-_:.]/.test(char)) {
      encoded += char;
    } else {
      // Convert Chinese or other Unicode characters to _uXXXX (Unicode escape)
      let code = char.charCodeAt(0).toString(16).padStart(4, '0');
      encoded += `_u${code}`;
    }
  }

  // Ensure the ID starts with a letter
  if (!/^[a-zA-Z]/.test(encoded)) {
    encoded = 'p' + encoded;
  }

  // Replace any remaining invalid sequences or multiple underscores
  encoded = encoded.replace(/[^a-zA-Z0-9-_:.]+/g, '_');

  // Ensure the ID is not empty after processing
  return encoded || 'p';
}

  function getBaseName(fullPath) {
    return fullPath.split('/').pop() || fullPath;
  }


  function generateCurvedPath(startX, startY, endX, endY) {
    const midX = (startX + endX) / 2;
    return `M ${startX} ${startY} C ${midX} ${startY}, ${midX} ${endY}, ${endX} ${endY}`;
  }

  function highlightConnections(elementId) {
    activeElement = elementId;
  }

  function clearHighlight() {
    activeElement = null;
  }

  function showElement(pdf_file) {
    dispatch('showElement', { pdf_file });
  }

  onMount(() => {
     if (!relation_data?.ratio_matrix) {
       console.error('relation_data or ratio_matrix is missing');
       return;
     }
     connections = [];
     fullnames = {};
     elements = {};
     Object.keys(relation_data.ratio_matrix).forEach( (x) => {
        elements[encodePathToHtmlId(x)] = getBaseName(x);
        fullnames[encodePathToHtmlId(x)] = x;
        Object.keys(relation_data.ratio_matrix[x]).forEach( (y) => {
            let a = encodePathToHtmlId(x);
            let b = encodePathToHtmlId(y);
            if (relation_data.ratio_matrix[x][y] > 0) {
                connections.push({
                   source: a,
                   target: b,
                   weight: relation_data.ratio_matrix[x][y]
                });
            }
        })
     })
  });

</script>

<div class="bg-white p-6 rounded-lg shadow-md">
  <div class="relative w-full h-full min-h-64 flex flex-col items-center">
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

          {@const isHighlighted = activeElement && (connection.source === activeElement)}

          <path
            d={generateCurvedPath(sourceX, sourceY, targetX, targetY)}
            fill="none"
            stroke={isHighlighted ? "#0d6efd" : "#d1d5db"}
            stroke-width={isHighlighted ? "4" : "2"}
            class="transition-all duration-300"
          />

          {#if isHighlighted}
              <text
                x={midX + 5}
                y={midY - 10}
                fill={isHighlighted ? "#0d6efd" : "#d1d5db"}
                class="text-sm font-medium"
              >
                {(connection.weight * 100).toFixed(3)}%
              </text>
          {/if}
        {/if}
      {/each}
    </svg>

    <div class="flex justify-between w-full mb-16">
      <div class="flex flex-col gap-8 pl-8 w-1/3">
        {#each Object.keys(elements) as elementId}
          <div
            id={`element-${elementId}`}
            class={`rounded-full px-6 py-3 text-center text-white text-sm font-medium inline-flex items-center justify-center cursor-pointer bg-orange-600 transition-all duration-300 hover:shadow-lg ${activeElement === elementId ? 'shadow-lg' : ''}`}
            on:mouseenter={() => highlightConnections(elementId)}
            on:mouseleave={clearHighlight}
            on:click={() => showElement(fullnames[elementId])}
          >
            {elements[elementId]}
          </div>
        {/each}
      </div>

      <div class="flex flex-col gap-8 pr-8 w-1/3">
        {#each Object.keys(elements) as elementId}
          <div
            id={`element-${elementId}-target`}
            class={`rounded-full px-6 py-3 text-center text-white text-sm font-medium inline-flex items-center justify-center bg-green-500 ${activeElement === elementId ? 'shadow-lg' : ''}`}
            on:mouseenter={() => highlightConnections(elementId)}
            on:mouseleave={clearHighlight}
          >
            {elements[elementId]}
          </div>
        {/each}
      </div>
    </div>
  </div>
</div>