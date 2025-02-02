input_dir = "";                                                                                           //your input image folder path
output_dir = "";                                                                                          //your output image folder path

File.makeDirectory(output_dir);
list = getFileList(input_dir);

for (i = 0; i < list.length; i++) {
 
    if (endsWith(list[i], ".tif")) {
        print("Processing: " + list[i]);
        
        run("Close All");
        wait(500);

        open(input_dir + list[i]);
        wait(1000);

        run("Trainable Weka Segmentation");
        wait(2000);
        
        call("trainableSegmentation.Weka_Segmentation.loadClassifier", "");   // in the second double quatation mark, you need to fill in your path 
        wait(1000);
        
        call("trainableSegmentation.Weka_Segmentation.getProbability");
        wait(3000);
        
        windows = getList("image.titles");
        for (j = 0; j < windows.length; j++) {
            if (indexOf(windows[j], "Probability") >= 0) {
                selectWindow(windows[j]);
                
                run("Duplicate...", "duplicate range=2");
                
                output_name = substring(list[i], 0, lengthOf(list[i])-4) + ".tif";
                
                saveAs("Tiff", output_dir + output_name);
                break;
            }
        }
        
        run("Close All");
        wait(1000);
       
        run("Collect Garbage");
        wait(500);
    }
   
    if (i % 10 == 0) {
        run("Close All");
        run("Collect Garbage");
        wait(2000);
    }
}

print("Processing complete!");