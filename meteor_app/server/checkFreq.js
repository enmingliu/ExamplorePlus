
import { ActionLog, Examples } from "./main";
import {PythonShell} from 'python-shell';

const get_frequent_dataset = async function(num_of_dataset){

    const pipeline = [
        {$group:{_id:"$dataset", count:{$sum: 1}}}
      ]
    const aggCursor = await ActionLog.rawCollection().aggregate(pipeline).toArray();
    let temp = [], res = [];
    if(aggCursor.length >= num_of_dataset){
        temp = [...aggCursor].sort((a,b) => b.count - a.count).slice(0, num_of_dataset);
    }
    for(let item of temp){
        res.push(item._id);
    } 

    return res;
}


const update_database = async function(){
    return new Promise((resolve, reject)=>{
        Examples.find().forEach(d => {

            if(urls.includes(d.dataset)){
                
                // referenced https://stackoverflow.com/questions/65988913/trying-to-get-data-from-python-shell-parsing-it-to-an-object-in-nodejs
                let options = {
                    mode: 'text',
                    pythonOptions: ['-u'], // get print results in real-time
                    args: [d.url]
                  };
        
                PythonShell.run('/Users/zacyou/Desktop/UCLA/Spring 2022/CS 230/Project/ExamplorePlus/Exampipe/get_info.py', options, function (err, res) {
                    if (err){
                        reject(err)
                    }else{
                        resolve(res)
                        // console.log(res)
                        if(d.num_stars !== res[1].num_stars){
                            Examples.update({_id: d_id}, {$set: { "num_stars": res[1].num_stars }});
                        }
                        if(d.num_forks !== res[1].num_forks){
                            Examples.update({_id: d_id}, {$set: { "num_forks": res[1].num_forks }});
                        }
                        if(d.num_open_issues !== res[1].num_open_issues){
                            Examples.update({_id: d_id}, {$set: { "num_open_issues": res[1].num_open_issues }});
                        }
                        if(d.num_contributors !== res[1].num_contributors){
                            Examples.update({_id: d_id}, {$set: { "num_contributors": res[1].num_contributors }});
                        }
                        if(d.num_closed_issues !== res[1].num_closed_issues){
                            Examples.update({_id: d_id}, {$set: { "num_closed_issues": res[1].num_closed_issues }});
                        }
                    }
                    
        
                });
        
            }
        
        })

    })
}
 
// let urls = await get_frequent_dataset(2);

// update_database()



