<script>
  import { onMount } from 'svelte';
  import { createEventDispatcher } from 'svelte';

  // Props
  export let relation_node = null;
  export let full_pdf_file = '';
  let short_pdf_file = '';
  let highlightedIndex = -1; // To track the highlighted item
  let selectSegment = null; // To store the clicked item
  const dispatch = createEventDispatcher();

  function getProgressColor(progress) {
    if (progress > 3) return 'bg-red-500';
    if (progress > 0.1) return 'bg-yellow-500';
    return 'bg-gray-500';
  }

  function getBaseName(fullPath) {
    return fullPath.split('/').pop() || fullPath;
  }

  // New function to truncate text
  function truncateText(text, maxLength = 32) {
    if (text.length > maxLength) {
      return text.slice(0, maxLength) + '...';
    }
    return text;
  }

  function handleRowClick(file) {
    //selectedItem = relation_node[file][0];
    selectSegment = [
       {
          file: full_pdf_file,
          block: relation_node[file][0][1]
       },
       {
          file: file,
          block: relation_node[file][0][2]
       }
    ]
    dispatch('showPdfImage', selectSegment);
  }

  $: short_pdf_file = getBaseName(full_pdf_file);

  onMount(() => {
  });
</script>

<div class="bg-white p-6 rounded-lg shadow-md mt-4">
  <h2 class="text-xl font-semibold mb-4">{short_pdf_file}</h2>
  <div class="overflow-x-auto">
    <table class="min-w-full divide-y divide-gray-200">
      <thead class="bg-gray-50">
        <tr>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">文字序列</th>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">相关文件</th>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">重复占比</th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-gray-200">
        {#each Object.keys(relation_node) as file, index}
          {#if relation_node[file].length > 0}
            <tr
              class:bg-gray-100={highlightedIndex === index}
              on:mouseover={() => (highlightedIndex = index)}
              on:mouseout={() => (highlightedIndex = -1)}
              on:click={() => handleRowClick(file)}
              style="cursor: pointer;"
            >
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {truncateText(relation_node[file][0][0])}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">
                  {getBaseName(file)}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="w-full bg-gray-200 rounded-full h-2.5">
                  <div
                    class="h-2.5 rounded-full {getProgressColor(relation_node[file][0][3] * 100)}"
                    style="width: {Math.floor(relation_node[file][0][3] * 100)}%"
                  ></div>
                </div>
                <span class="text-xs text-gray-500 mt-1">{Math.round(relation_node[file][0][3] * 100000) / 1000}%</span>
              </td>
            </tr>
          {/if}
        {/each}
      </tbody>
    </table>
  </div>
</div>