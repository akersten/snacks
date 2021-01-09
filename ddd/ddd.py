import os, argparse


def vals_are_same(offset, *content):
    """
    Determine if the values at offset of the content arrays are all the same.
    :param offset: The offset into the content arrays to check.
    :param content: The content arrays.
    :return: True if content[0][offset] == content[1][offset] == ..., False otherwise.
    """
    check = None
    for arr in content:
        if check is None:  # Initialize check value with value from first content array.
            check = arr[offset]
            continue
        if check == arr[offset]:
            continue
        return False
    return True


def vals_are_unique(offset, *content):
    """
    Determine if the values at offset of the content arrays are all unique.
    :param offset: The offset into the content arrays to check.
    :param content: The content arrays.
    :return: True if content[0][offset] != content[1][offset] != ..., False otherwise.
    """
    uniques = set()
    for arr in content:
        check = arr[offset]
        if check in uniques:
            return False
        uniques.add(check)
    return True


def vals_to_array(offset, *content):
    """
    Slice all the values at an offset from the content arrays into an array.
    :param offset: The offset into the content arrays to slice.
    :param content: The content arrays.
    :return: An array of all the values of content[*][offset].
    """
    slice = []
    for arr in content:
        slice.append(arr[offset])
    return slice


def diffs(size, *content):
    """
    Calculate all-different and some-different lists of each byte array.
    :param size: The length, in bytes, of the content arrays.
    :param content: A list of content arrays.
    :return: A tuple of arrays containing signal offset data and noise offset data: (signal_data[], noise_data[])
             The offset arrays themselves contain tuples containing the offset and the data from each content array at
             that offset: (offset, content[0][offset], content[1][offset], ...)
    """
    signal_data = []
    noise_data = []

    for i in range(0, size):
        if vals_are_same(i, *content):
            continue
        if vals_are_unique(i, *content):
            noise_data.append((i, *vals_to_array(i, *content)))
            continue
        signal_data.append((i, *vals_to_array(i, *content)))

    return signal_data, noise_data


def output_line(data, decimal):
    """
    Print an (offset, values...) tuple.
    :param data: A tuple in the form (offset, *values) to print.
    :param decimal: True to format output values as decimal, False to format output values as hex.
    """
    data_vals = ""
    for val in data[1:]:
        data_vals += "{:02x} ".format(val) if not decimal else "{:03} ".format(val)
    data_vals = data_vals.rstrip()

    print("{:08x}: {}".format(data[0], data_vals))


def output_passes_filter(data, filter_from, filter_to):
    """
    Check if the data passes the given filter.
    :param data: The data tuple to check.
    :param filter_to: Filter to only values starting from this value...
    :param filter_from: ...Filter to only values ending with this value.
    :return: True if the data passes the filter, False otherwise.
    """
    if filter_from is None or filter_to is None:
        return True

    return data[1] == filter_from and data[2] == filter_to


def output(signal_data, noise_data, filter_from, filter_to, decimal):
    """
    Print the results of the signal and noise data.
    :param signal_data: The list of signal data.
    :param noise_data: The list of noise data.
    :param filter_to: Filter to only values starting from this value...
    :param filter_from: ...Filter to only values ending with this value.
    :param decimal: True to format output values as decimal, False to format output values as hex.
    """

    if len(noise_data) > 0 and filter_from is None and filter_to is None:
        print("Noise (all files differ):")
        for data in noise_data:
            output_line(data, decimal)

    if len(signal_data) > 0:
        print("Signal (identical values across some but not all files):")
        for data in signal_data:
            if output_passes_filter(data, filter_from, filter_to):
                output_line(data, decimal)


def main():
    parser = argparse.ArgumentParser("ddd")
    parser.add_argument("file1", help="The first file to compare.", type=str)
    parser.add_argument("file2", help="The second file to compare.", type=str)
    parser.add_argument("file3", help="The third file to compare.", type=str)
    parser.add_argument("vfrom", help="Filter the output to show a value change from this value.", type=int,
                        default=None, nargs="?")
    parser.add_argument("vto", help="Filter the output to show a value change to this value.", type=int, default=None,
                        nargs="?")
    parser.add_argument("-d", help="Set to format output values as decimal instead of hex.", action="store_true")
    args = parser.parse_args()

    size1 = os.stat(args.file1).st_size
    size2 = os.stat(args.file2).st_size
    size3 = os.stat(args.file3).st_size

    if size1 != size2 or size2 != size3:
        print("File lengths differ: {} {} {}".format(size1, size2, size3))
        quit(1)

    size = size1
    with open(args.file1, "rb") as f1, open(args.file2, "rb") as f2, open(args.file3, "rb") as f3:
        # XXX: Assume the files are small; buffer if it gets unwieldy.
        signal_data, noise_data = diffs(size, f1.read(), f2.read(), f3.read())

    output(signal_data, noise_data, args.vfrom, args.vto, args.d)


if __name__ == "__main__":
    main()
