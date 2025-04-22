<script>
  // Props
  export let isLoading = false;
  export let allFilesIndexed = false;
  
  // Events
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();
  
  let fileInput;
  let file;
  
  function handleFileChange(event) {
    file = event.target.files[0];
  }
  
  function handleUpload() {
    if (!file) return;
    dispatch('upload', { file });
  }
  
  function handleCleanup() {
    dispatch('cleanup');
  }
  
  function handleScan() {
    dispatch('scan');
  }

  function handleCompare() {
    dispatch('compare');
  }

  // Function to reset the file input (can be called from parent)
  export function resetFileInput() {
    file = null;
    if (fileInput) fileInput.value = '';
  }
</script>

<div class="bg-white p-6 rounded-lg shadow-md">
  <h2 class="text-xl font-semibold mb-4">请在此上传zip文件</h2>
  <input
    type="file"
    accept=".zip"
    bind:this={fileInput}
    on:change={handleFileChange}
    class="block w-full text-sm text-gray-500
      file:mr-4 file:py-2 file:px-4
      file:rounded-full file:border-0
      file:text-sm file:font-semibold
      file:bg-blue-50 file:text-blue-700
      hover:file:bg-blue-100"
  />
  <div class="mt-4 space-x-4">
    <button
      on:click={handleUpload}
      disabled={!file || isLoading}
      class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50"
    >
      上传到缓冲区
    </button>
    <button
      on:click={handleCleanup}
      disabled={isLoading}
      class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 disabled:opacity-50"
    >
      清空缓冲区
    </button>
    <button
      on:click={handleScan}
      disabled={isLoading}
      class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 disabled:opacity-50"
    >
      扫描文件
    </button>
    <button
      on:click={handleCompare}
      disabled={isLoading || !allFilesIndexed}
      class="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600 disabled:opacity-50"
    >
      比较文件
    </button>
  </div>
</div> 