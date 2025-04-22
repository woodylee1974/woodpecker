<script>
  import { onMount, tick, setContext } from 'svelte';
  import FileUpload from './components/FileUpload.svelte';
  import FileList from './components/FileList.svelte';
  
  let status = '';
  let comparisonResults = [];
  let isLoading = false;
  let fileStatuses = {};
  let allFilesIndexed = false;
  let pdf_files = [];

  onMount(async () => {
    fileList.collectInfo();
  })
  
  async function handleUpload(event) {
    const { file } = event.detail;
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      isLoading = true;
      const response = await fetch('http://localhost:8000/backend/upload', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      status = data.message || data.error;
    } catch (error) {
      status = 'Error uploading file: ' + error.message;
    } finally {
      isLoading = false;
    }
  }
  
  async function handleCleanup() {
    try {
      isLoading = true;
      const response = await fetch('http://localhost:8000/backend/cleanup', {
        method: 'POST'
      });
      const data = await response.json();
      uploadStatus = data.message;
      
      // Reset state
      fileStatuses = {};
      allFilesIndexed = false;
      fileList.stopPolling();
      fileUpload.resetFileInput();
    } catch (error) {
      status = '清空缓冲区出错: ' + error.message;
    } finally {
      isLoading = false;
    }
  }
  
  async function handleScan() {
    try {
      isLoading = true;
      const response = await fetch('http://localhost:8000/backend/scan', {
        method: 'POST'
      });
      const data = await response.json();

      if (data.message) {
        // Start polling for file status
        fileList.startPolling();
      }
    } catch (error) {
      status = '扫描文件出错: ' + error.message;
    } finally {
      isLoading = false;
    }
  }

  async function handleCompare() {
    try {
      isLoading = true;
      const response = await fetch('http://localhost:8000/backend/compare', {
        method: 'POST'
      });
      const data = await response.json();
    } catch (error) {
      status = '生成检查结果出错: ' + error.message;
    } finally {
      isLoading = false;
    }
  }


  function handleStatusUpdate(event) {
    const { fileStatuses: newFileStatuses, allFilesIndexed: newAllFilesIndexed } = event.detail;
    fileStatuses = newFileStatuses;
    allFilesIndexed = newAllFilesIndexed;
  }
  
  let fileUpload;
  let fileList;
</script>

<main class="container mx-auto px-4 py-8">
  <h1 class="text-3xl font-bold mb-8">Text Compare</h1>
  
  <div class="space-y-6">
    <FileUpload
      bind:this={fileUpload}
      {isLoading}
      {allFilesIndexed}
      on:upload={handleUpload}
      on:cleanup={handleCleanup}
      on:scan={handleScan}
    />
    
    <FileList
      bind:this={fileList}
      {fileStatuses}
      {allFilesIndexed}
      on:statusUpdate={handleStatusUpdate}
    />
    
    {#if status}
      <div class="bg-gray-100 p-4 rounded">
        <p class="text-gray-700">{status}</p>
      </div>
    {/if}
    
    {#if comparisonResults.length > 0}
      <div class="bg-white p-6 rounded-lg shadow-md">
        <h2 class="text-xl font-semibold mb-4">Similar Segments</h2>
        <div class="space-y-4">
          {#each comparisonResults as result}
            <div class="border p-4 rounded">
              <p class="font-medium">{result}</p>
            </div>
          {/each}
        </div>
      </div>
    {/if}
  </div>
</main>

<style>
  :global(body) {
    background-color: #f3f4f6;
  }
</style> 