<script>
  import { onMount, tick, setContext } from 'svelte';
  import FileUpload from './components/FileUpload.svelte';
  import FileList from './components/FileList.svelte';
  import RelationView from './components/RelationView.svelte';
  import SegmentView from './components/SegmentView.svelte';
  import ImagePair from './components/ImagePair.svelte';
  
  let status = '';
  let isLoading = false;
  let fileStatuses = {};
  let allFilesProcessed = false;
  let partialFilesProcessed = false;
  let pdf_files = [];
  let relation_data = null;
  let relation_node = null;
  let full_pdf_file = '';
  let leftSrc = null;
  let rightSrc = null;
  let selectSegment = null;

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
      allFilesProcessed = false;
      partialFilesProcessed = false;
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
        method: 'GET'
      });
      relation_data = await response.json();
    } catch (error) {
      status = '生成检查结果出错: ' + error.message;
    } finally {
      isLoading = false;
    }
  }


  function handleStatusUpdate(event) {
    const { fileStatuses: newFileStatuses, allFilesProcessed: newAllFilesProcessed, partialFilesProcessed: newPartialFilesProcessed } = event.detail;
    fileStatuses = newFileStatuses;
    allFilesProcessed = newAllFilesProcessed;
    partialFilesProcessed = newPartialFilesProcessed;
  }

  function showElement(event) {
    const { pdf_file } = event.detail;
    full_pdf_file = pdf_file;
    relation_node = relation_data.relation_matrix[pdf_file];
  }

  async function showPdfImage(event) {
    selectSegment = event.detail;
    try {
      const response = await fetch('http://localhost:8000/backend/get_pdf_pair', {
        method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
        body: JSON.stringify(selectSegment)
      });
      const data = await response.json();
      leftSrc = `data:image/png;base64,${data.left_image}`;
      rightSrc = `data:image/png;base64,${data.right_image}`;
      status = data.message;
    } catch (error) {
      status = '取PDF出错: ' + error.message;
    } finally {
    }
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
      {allFilesProcessed}
      {partialFilesProcessed}
      on:upload={handleUpload}
      on:cleanup={handleCleanup}
      on:scan={handleScan}
      on:compare={handleCompare}
    />
    
    <FileList
      bind:this={fileList}
      {fileStatuses}
      {allFilesProcessed}
      {partialFilesProcessed}
      on:statusUpdate={handleStatusUpdate}
    />
    
    {#if status}
      <div class="bg-gray-100 p-4 rounded">
        <p class="text-gray-700">{status}</p>
      </div>
    {/if}

    {#if relation_data}
    <RelationView
       {relation_data}
       on:showElement={showElement}
    />
    {/if}

    {#if relation_node}
    <SegmentView
       {relation_node}
       {full_pdf_file}
       on:showPdfImage={showPdfImage}
    />
    {/if}

    {#if leftSrc !== null && rightSrc !== null}
    <ImagePair
       {leftSrc}
       {rightSrc}
       bind:selectSegment={selectSegment}
    />
    {/if}

  </div>
</main>

<style>
  :global(body) {
    background-color: #f3f4f6;
  }
</style> 