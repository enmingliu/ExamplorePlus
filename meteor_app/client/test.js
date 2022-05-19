
// let file = require('../private/addActionListener.json');
// let json = JSON.parse(JSON.stringify(file))


function getUrl(filename){
    var file = require('../private/' + filename);
    var json = JSON.parse(JSON.stringify(file));
    var result_urls = []
    for(var i = 0; i < json.length; i++){
       result_urls.push(json[i].url);
    }

    return result_urls;
}

function trim_repo_url(array){
    var repo_url = array;
    for(var i = 0; i < array.length; i++){
        for(var j = 0; j < array[i].length; j++){
            repo_url[i][j] = [(array[i][j].substring(0, array[i][j].indexOf('tree')-1)), array[i][j].substring(array[i][j].indexOf('master')+7, array[i][j].length)]
        }
    }

    return repo_url;
}

const returnAllUrls = async(directory, res) => {

    const Promise = require('bluebird');
    const fs = Promise.promisifyAll(require('fs'));

    fs.readdirAsync(directory).then((filename)=>{
        for(const item of filename){
            res.push(getUrl(item));
        }
        var repo_url = trim_repo_url(res);
        var path = '/Users/zacyou/Desktop/UCLA/Spring 2022/CS 230/Project/Examplore-master/meteor_app/client/'
        var name = 'output.txt';
        var path_for_repo_url = '/Users/zacyou/Desktop/UCLA/Spring 2022/CS 230/Project/Examplore-master/meteor_app/client/';

        for(let i = 0; i < repo_url.length; i++){
            console.log(JSON.stringify(repo_url[1][i][1])+",")
        }
        fs.writeFileSync(path + name, res.toString(), (err) => {
      
            // In case of a error throw err.
            if (err) throw err;
        })

        
        
        for(let i = 0; i < repo_url.length; i++){
            var obj = {};
            for(let j = 0; j < repo_url[i].length; j++){
                obj[repo_url[i][j][0]] = repo_url[i][j][1];
                fs.writeFileSync(path_for_repo_url + filename[i], JSON.stringify(obj), (err) => {
              
                        // In case of a error throw err.
                    if (err) throw err;
                })
                
            }
            // console.log(obj);

        }
        
        return res;
    })
    
   
    

}
var directory = '/Users/zacyou/Desktop/UCLA/Spring 2022/CS 230/Project/Examplore-master/meteor_app/private';

returnAllUrls(directory, []);





