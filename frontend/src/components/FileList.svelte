<script>
  import { onMount, onDestroy } from 'svelte';
  import FileStatusTable from './FileStatusTable.svelte';
  
  // Props
  export let fileStatuses = {};
  export let allFilesIndexed = false;
  
  // Events
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();
  
  let statusInterval;
  
  // Convert fileStatuses object to array format expected by FileStatusTable
  $: files = Object.entries(fileStatuses).map(([name, status]) => ({
    name,
    status: status.status,
    progress: status.progress
  }));
  
  // Start polling for file status
  function startStatusPolling() {
    // Clear any existing interval
    if (statusInterval) {
      clearInterval(statusInterval);
    }
    
    // Poll for status updates every 1 second
    statusInterval = setInterval(async () => {
      try {
        const response = await fetch('http://localhost:8000/backend/file-status');
        const data = await response.json();
        fileStatuses = data.files;
        allFilesIndexed = data.all_indexed;
        
        // Dispatch event to parent component
        dispatch('statusUpdate', { fileStatuses, allFilesIndexed });
        
        // If all files are indexed, stop polling
        if (allFilesIndexed) {
          clearInterval(statusInterval);
        }
      } catch (error) {
        console.error('Error fetching file status:', error);
      }
    }, 1000);
  }
  
  // Clean up interval when component is destroyed
  onDestroy(() => {
    if (statusInterval) {
      clearInterval(statusInterval);
    }
  });
  
  // Start polling when component is mounted
  onMount(() => {
    if (Object.keys(fileStatuses).length > 0) {
      startStatusPolling();
    }
  });
  
  // Function to manually start polling (can be called from parent)
  export function startPolling() {
    startStatusPolling();
  }
  
  // Function to stop polling (can be called from parent)
  export function stopPolling() {
    if (statusInterval) {
      clearInterval(statusInterval);
    }
  }
</script>

{#if files.length > 0}
  <FileStatusTable {files} />
{/if} 