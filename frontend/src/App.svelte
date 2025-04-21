<script>
  let fileInput;
  let file;
  let uploadStatus = '';
  let comparisonResults = [];
  let isLoading = false;

  function handleFileChange(event) {
    file = event.target.files[0];
  }

  async function handleFileUpload() {
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
      console.log(data)
      uploadStatus = data.message || data.error;
    } catch (error) {
      uploadStatus = 'Error uploading file: ' + error.message;
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
      file = null;
      if (fileInput) fileInput.value = '';
    } catch (error) {
      uploadStatus = 'Error cleaning up: ' + error.message;
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
      comparisonResults = data.similar_segments || [];
      uploadStatus = 'Comparison completed';
    } catch (error) {
      uploadStatus = 'Error comparing files: ' + error.message;
    } finally {
      isLoading = false;
    }
  }
</script>

<main class="container mx-auto px-4 py-8">
  <h1 class="text-3xl font-bold mb-8">Text Comparison Tool</h1>
  
  <div class="space-y-6">
    <div class="bg-white p-6 rounded-lg shadow-md">
      <h2 class="text-xl font-semibold mb-4">Upload ZIP File</h2>
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
          on:click={handleFileUpload}
          disabled={!file || isLoading}
          class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50"
        >
          Upload
        </button>
        <button
          on:click={handleCleanup}
          disabled={isLoading}
          class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 disabled:opacity-50"
        >
          Clean Up
        </button>
        <button
          on:click={handleCompare}
          disabled={isLoading}
          class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 disabled:opacity-50"
        >
          Compare Files
        </button>
      </div>
    </div>

    {#if uploadStatus}
      <div class="bg-gray-100 p-4 rounded">
        <p class="text-gray-700">{uploadStatus}</p>
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