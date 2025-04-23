<script>
  export let leftSrc;
  export let rightSrc;
</script>

<div class="bg-white p-6 rounded-lg shadow-md">
    <div class="image-comparison">
      <div class="image-container left">
        <img src={leftSrc} alt="Left Image" />
      </div>
      <div class="image-container right">
        <img src={rightSrc} alt="Right Image" />
      </div>
    </div>
</div>

<style>
  .image-comparison {
    display: flex;
    width: 100%; /* Make the container take full width */
    height: auto; /* Adjust height based on content */
  }

  .image-container {
    flex: 1; /* Distribute available space equally */
    display: flex;
    justify-content: center; /* Center the image horizontally */
    align-items: center; /* Center the image vertically */
    overflow: hidden; /* Prevent image from overflowing the container */
    padding: 5px; /* Optional padding between images */
  }

  img {
    display: block; /* Remove extra space below the image */
    max-width: 100%; /* Ensure image doesn't exceed container width */
    max-height: 100%; /* Ensure image doesn't exceed container height */
    object-fit: contain; /* Maintain aspect ratio and fit within container */
  }
</style>