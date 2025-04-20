get_percentage = 0.06

convert_int = get_percentage * 100
convert_int2 = int(convert_int)
conv_string = f"{convert_int2}%"
once = f"{int(get_percentage * 100)}%"

print("get_percentage", get_percentage)
print("convert_int", convert_int)
print("convert_int", (convert_int2))
print("conv_string", conv_string)
print("once", once)