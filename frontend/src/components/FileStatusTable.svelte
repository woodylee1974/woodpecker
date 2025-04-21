<script>
  // Props
  export let files = [];
  
  // Helper function to get status color
  function getStatusColor(status) {
    switch (status.state) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'processing':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  }
  
  // Helper function to get progress bar color
  function getProgressColor(progress) {
    if (progress === 100) return 'bg-green-500';
    if (progress > 50) return 'bg-blue-500';
    if (progress > 25) return 'bg-yellow-500';
    return 'bg-gray-500';
  }
</script>

<div class="bg-white p-6 rounded-lg shadow-md mt-4">
  <h2 class="text-xl font-semibold mb-4">File Processing Status</h2>
  <div class="overflow-x-auto">
    <table class="min-w-full divide-y divide-gray-200">
      <thead class="bg-gray-50">
        <tr>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">File Name</th>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Progress</th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-gray-200">
        {#each files as file}
          <tr>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{file.name}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span class={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(file.status)}`}>
                {file.status.message}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="w-full bg-gray-200 rounded-full h-2.5">
                <div
                  class={`h-2.5 rounded-full ${getProgressColor(file.progress)}`}
                  style="width: {file.progress}%"
                ></div>
              </div>
              <span class="text-xs text-gray-500 mt-1">{file.progress}%</span>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div> 