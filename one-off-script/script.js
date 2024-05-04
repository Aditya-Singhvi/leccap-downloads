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