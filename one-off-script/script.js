// Author: Ajay Pillay

// Run the following in the browser console of the course page
// (where you can see links to all the recordings). 

var links = "";

await Promise.all(recordings.map(async (lec) => {
    const res = await fetch(`https://leccap.engin.umich.edu/leccap/viewer/api/product/?rk=${lec.url.replace('/leccap/player/r/', '')}`, {
  "credentials": "include"});
    const data = await res.json();
    lec.url = `https:${data.mediaPrefix}${data.sitekey}/${data.info.movie_exported_name}.${data.info.movie_type}`;
    links += `Lecture_${lec.defaultSort}.mp4 "${lec.url}"\n`;
}));
var a = document.createElement("a");
var file = new Blob([links], {type: "text/plain"});
a.href = URL.createObjectURL(file);
a.download = "links.txt";
a.click();

// Once this is done:
//  (1) Navigate to the directory with links.txt in your terminal. 
//  (2) Run 
//          xargs < links.txt -P 0 -L 1 wget -O 
//      to start downloading all recordings in parallel. You can change 
//      -P 0 to -P 4 or any desired value to limit the number of concurrent 
//      downloads. When set to 0, this runs as many as it can. 
