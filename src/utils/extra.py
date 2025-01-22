



def mask_name(name: str) -> str:
    parts = name.split()
    masked_parts = []  # List to hold the masked parts

    for part in parts:
        if len(part) > 1:
            # Mask all but the first character of each part
            masked_parts.append(part[0] + '*' * (len(part) - 1))
        else:
            # If the part is a single character, no masking is needed
            masked_parts.append(part)

    return ' '.join(masked_parts)  # Join the list of masked parts back into a string
