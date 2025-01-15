import cv2
import numpy as np

# Load the image
image = cv2.imread('input.jpg')

# Load the mask (assuming it has the same dimensions as the image)
mask = cv2.imread('mask.jpg')

# Resize the mask to match the image dimensions (optional)
mask = cv2.resize(mask, (image.shape[1], image.shape[0]))

# Create a pixelated version of the original image
pixelated_image = cv2.resize(image, (16, 16), interpolation=cv2.INTER_NEAREST)
pixelated_image = cv2.resize(pixelated_image, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST)

# Apply the mask to the original image
masked_image = cv2.bitwise_and(image, mask)

# Invert the mask
inverted_mask = cv2.bitwise_not(mask)

# Combine the masked image and pixelated image
result_image = cv2.bitwise_or(masked_image, cv2.bitwise_and(pixelated_image, inverted_mask))

# Display the result
cv2.imshow('Result Image', result_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Save the result
cv2.imwrite('output.jpg', result_image)