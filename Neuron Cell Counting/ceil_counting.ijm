directory = "";                                 //your image folder path
filelist = getFileList(directory);

setBatchMode("hide"); // do not show process to speed up
roiManager("reset"); // clear ROI Manager
run("Clear Results"); // clear result table


imageNames = newArray(0);
cellCounts = newArray(0);
currentRow = 0;

for (i = 0; i < lengthOf(filelist); i++) {
    if (endsWith(filelist[i], ".jpg")) { 
        open(directory + filelist[i]);
        title = getTitle();
        run("8-bit");
        //run("Enhance Contrast", "saturated=0.35");
        run("Command From Macro", "command=[de.csbdresden.stardist.StarDist2D], args=['input':" + title + ", 'modelChoice':'Versatile (fluorescent nuclei)', 'normalizeInput':'true', 'percentileBottom':'29.400000000000002', 'percentileTop':'100.0', 'probThresh':'0.479071', 'nmsThresh':'0.3', 'outputType':'ROI Manager', 'nTiles':'1', 'excludeBoundary':'2', 'roiPosition':'Automatic', 'verbose':'false', 'showCsbdeepProgress':'false', 'showProbAndDist':'false'], process=[false]");                            //can be ajusted according to your images' characteristics
        
        roiCount = roiManager("count");      // start to count the ceils
        for (j = roiCount-1; j >= 0; j--) {
            roiManager("select", j);
            run("Measure");
            area = getResult("Area", nResults-1);
            if (area < 500) {
                roiManager("delete");
            }
        }
        run("Clear Results");
        
        cellNum = roiManager("count"); // get ROI number after filtering
        
        // Add the result into the form
        imageNames = Array.concat(imageNames, title);
        cellCounts = Array.concat(cellCounts, cellNum);
        
        close(); // close the current image
        roiManager("reset"); // clear ROI Manager
    } 
}

// Create a form to show all of the results
for (i = 0; i < imageNames.length; i++) {
    setResult("Image Name", i, imageNames[i]);
    setResult("Cell Number", i, cellCounts[i]);
}

updateResults(); // Update the result form