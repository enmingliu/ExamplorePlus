const fs = require('fs');
const path = require('path');

const trim = function(url){
    const trimmed_url = {};
    trimmed_url[url.substring(0, url.indexOf('tree')-1)] = url.substring(url.indexOf('master')+7, url.length)
    return trimmed_url;
}

// const readFromFolder = function(dir){
//     const obj = {};
    
//     const jsonsInDir = fs.readdirSync(dir).filter(file => path.extname(file) === '.json');
//     jsonsInDir.forEach(file => {
//         const fileData = fs.readFileSync(path.join(dir, file));
//         const json = JSON.parse(fileData.toString());

//         json.forEach(item => {
//             if(!obj[item.dataset]){
//                 obj[item.dataset] = [];
//                 obj[item.dataset].push(trim(item.url));
//             }else
//                 obj[item.dataset].push(trim(item.url));
//         })
        
//       });

//       return obj;
// }

const writeToFile = function(input, dir){
    for (const key in input) {
        const str = JSON.stringify(input[key]);
        const content = "{" + str.replace(/\[/g, "").replace(/\]/g,"").replace(/{/g,"").replace(/}/g,"") + "}"
    
        fs.writeFileSync(dir + key + ".json", content, (err) => {
            if (err) {
              console.error(err)
              return
            }
            //file written successfully
          })
    }
}


var directory = '/Users/zacyou/Desktop/UCLA/Spring 2022/CS 230/Project/ExamplorePlus/meteor_app/private';

// var app = readFromFolder(directory);
// writeToFile(app, '/Users/zacyou/Desktop/UCLA/Spring 2022/CS 230/Project/ExamplorePlus/boa/backend/sampleJSON');






