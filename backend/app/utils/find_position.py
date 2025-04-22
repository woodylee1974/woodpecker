def find_index_by_value(arr, target):
    # Create list of (value, index) pairs
    indexed_arr = list(enumerate(arr))
    # Sort by value
    indexed_arr.sort(key=lambda x: x[1])

    # Handle edge cases
    if not arr or target < indexed_arr[0][1]:
        return -1
    if target > indexed_arr[-1][1]:
        return indexed_arr[-1][1]

    # Binary search
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        curr_val = indexed_arr[mid][1]

        # Check if target is between current and next value
        if mid < len(arr) - 1 and curr_val <= target < indexed_arr[mid + 1][1]:
            return indexed_arr[mid][1]
        # Check if target equals current value
        elif curr_val == target:
            return indexed_arr[mid][1]
        elif curr_val < target:
            left = mid + 1
        else:
            right = mid - 1

    # If we reach here, target is between the last checked values
    return indexed_arr[right][1]


# Example usage
if __name__ == "__main__":
    arr = [4, 0, 9, 10]
    test_values = [7, 0, 11, -1, 8, 3]

    for val in test_values:
        result = find_index_by_value(arr, val)
        print(f"Value {val} -> Index {result}")