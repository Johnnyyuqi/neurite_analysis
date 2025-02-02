import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import pandas as pd  # 用于保存到Excel

# set the folder path

folder1 = 'd:\\downloads\\temp\\neurite\\2025.1.9 iMN staining QC\\Set 1\\green_process\\'  # original image
folder2 = 'd:\\downloads\\temp\\neurite\\2025.1.9 iMN staining QC\\Set 1\\green_process_new\\'  # image after enhancement 
output_folder = 'd:\\downloads\\temp\\neurite\\2025.1.9 iMN staining QC\\Set 1\\neurite_area_analysis_result\\'  # folder to save images


# guarantee the output folder exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)


files1 = glob.glob(os.path.join(folder1, '*.tif'))
print(f'Found {len(files1)} files in {folder1}')


grouped_results = {}

# Traverse each file

for file1 in files1:
    filename = os.path.basename(file1)
    base_name = os.path.splitext(filename)[0]
    group_key = base_name[:3]  
    file2 = os.path.join(folder2, f'{base_name}.tif')

    if os.path.exists(file2):
        print(f'Found corresponding file {file2}')
 
    
        neurite_image = cv2.imread(file1, -1)
        neurite_image_rgb = cv2.cvtColor(neurite_image, cv2.COLOR_BGR2RGB)
        binary_neurite_image = cv2.imread(file2, -1)

 
        # Same process as the demo
        # ret, binary_neurite_image_1 = cv2.threshold(binary_neurite_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU) # if binary_neurite_image.dtype == np.uint16:
        if binary_neurite_image.dtype == np.uint16:
            binary_neurite_image = cv2.normalize(binary_neurite_image, None, 0, 255, cv2.NORM_MINMAX)
            binary_neurite_image = binary_neurite_image.astype(np.uint8)
        elif binary_neurite_image.dtype == np.float32 or binary_neurite_image.dtype == np.float64:
            binary_neurite_image = cv2.normalize(binary_neurite_image, None, 0, 255, cv2.NORM_MINMAX)
            binary_neurite_image = binary_neurite_image.astype(np.uint8)
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))  
        contrast_enhanced = clahe.apply(binary_neurite_image)

        denoised_image = cv2.GaussianBlur(contrast_enhanced, (3, 3), 0)

        _, otsu_binary = cv2.threshold(denoised_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        adaptive_binary = cv2.adaptiveThreshold(
            denoised_image, 
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,  
            2   
        )

        combined_binary = cv2.bitwise_and(otsu_binary, adaptive_binary)

        kernel_small = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        kernel_medium = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

        opened = cv2.morphologyEx(combined_binary, cv2.MORPH_OPEN, kernel_small)

        morphed_image = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel_medium)

        # Compute the ratio of the white area
        original_white_pixels = np.sum(morphed_image== 255)
        total_pixels = binary_neurite_image.size
        area_ratio = (original_white_pixels / total_pixels) * 100

        if group_key not in grouped_results:
            grouped_results[group_key] = []
        grouped_results[group_key].append(area_ratio)

        fig, axs = plt.subplots(1, 2, figsize=(12, 6))
        axs[0].imshow(neurite_image_rgb)
        axs[0].axis('off')
        axs[0].set_title('Initial Image')
        axs[1].imshow(morphed_image, cmap='gray')
        axs[1].axis('off')
        axs[1].set_title('Processed Image')
        plt.figtext(0.5, 0.01, f"The percentage of the neurite in the whole image is: {area_ratio:.2f}%", ha='center', fontsize=12)
        
        # save images
        output_path = os.path.join(output_folder, f'{base_name}_comparison.png')
        plt.savefig(output_path)
        plt.close()
        print(f'Comparison image saved to {output_path}')
        
# write the results into the excel
excel_path = os.path.join(output_folder, 'area_ratios.xlsx')
with pd.ExcelWriter(excel_path) as writer:
    for group_key, ratios in grouped_results.items():
        df = pd.DataFrame([ratios], columns=[f'Image {i+1}' for i in range(len(ratios))])
        df.to_excel(writer, sheet_name=group_key, index=False)

print(f'Area ratios saved to {excel_path}')