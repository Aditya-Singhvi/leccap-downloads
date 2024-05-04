// Author: Ajay Pillay

// Run the following in the browser console of the course page
// (where you can see links to all the recordings). 

var links = "";

await Promise.all(recordings.map(async (lec) => {
    const res = await fetch(`https://leccap.engin.umich.edu/leccap/viewer/api/product/?rk=${lec.url.replace('/leccap/player/r/', '')}`, {
  "credentials": "include"});
    const data = await res.json();
    lec.url = `https:${data.med