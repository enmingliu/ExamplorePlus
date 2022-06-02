
import { ActionLog, Examples } from "./main.js";
import { PythonShell } from 'python-shell';

const bound = Meteor.bindEnvironment((callback) => { callback(); });

export const get_frequent_dataset = async function () {

    const pipeline = [
        { $group: { _id: "$dataset", count: { $sum: 1 } } }
    ]
    const aggCursor = await ActionLog.rawCollection().aggregate(pipeline).toArray();
    let temp = [], res = [];

    temp = [...aggCursor].sort((a, b) => b.count - a.count).slice(0, aggCursor.length > 5 ? 5 : aggCursor.length); // max 5 popular apis checking

    for (let item of temp) {
        res.push(item._id);
    }

    return res;
}



export const update_database = async function (urls) {
    return new Promise((resolve, reject) => {
        let x = 0;
        Examples.find().forEach(d => {

            if (urls.includes(d.dataset)) {
                if (d.num_stars && d.num_forks && d.num_open_issues && d.num_contributors && d.num_closed_issues && d.timestamp) {
                    let options = {
                        mode: 'text',
                        pythonOptions: ['-u'], // get print results in real-time
                        args: [d.url]
                    };

                    PythonShell.run('/Users/zacyou/Desktop/UCLA/Spring 2022/CS 230/Project/ExamplorePlus/Exampipe/get_info.py', options, function (err, res) {
                        if (err) {
                            reject(err)
                        } else {
                            resolve(res)
                            let obj = JSON.parse(res[0].replace(/'/g, '"'));
                            let isChange = false;
//                             console.log(res);
//                             console.log(res[0]);
//                             console.log(d.num_stars, obj.num_stars, d.num_stars === obj.num_stars)
//                             console.log(d.num_forks, obj.num_forks, d.num_forks === obj.num_forks)
//                             console.log(d.num_open_issues, obj.num_open_issues, d.num_open_issues === obj.num_open_issues)
//                             console.log(parseInt(d.num_contributors), parseInt(obj.num_contributors), parseInt(d.num_contributors) === parseInt(obj.num_contributors))
//                             console.log(d.num_closed_issues, obj.num_closed_issues, d.num_closed_issues === obj.num_closed_issues)
//                             console.log(d.timestamp, obj.last_commit, d.timestamp === obj.last_commit)

                            if (d.num_stars && d.num_stars !== obj.num_stars) {
                                bound(() => {
                                    Examples.update({ _id: d._id }, { $set: { "num_stars": obj.num_stars } });
                                })
                                isChange = true;
                            }
                            if (d.num_forks && d.num_forks !== obj.num_forks) {
                                bound(() => {
                                    Examples.update({ _id: d._id }, { $set: { "num_forks": obj.num_forks } });
                                })
                                isChange = true;
                            }
                            if (d.num_open_issues && d.num_open_issues !== obj.num_open_issues) {
                                bound(() => {
                                    Examples.update({ _id: d._id }, { $set: { "num_open_issues": obj.num_open_issues } });
                                })
                                isChange = true;
                            }
                            if (d.num_contributors && parseInt(d.num_contributors) !== parseInt(obj.num_contributors)) {
                                bound(() => {
                                    Examples.update({ _id: d._id }, { $set: { "num_contributors": parseInt(obj.num_contributors) } });
                                })
                                isChange = true;
                            }
                            if (d.num_closed_issues && d.num_closed_issues !== obj.num_closed_issues) {
                                bound(() => {
                                    Examples.update({ _id: d._id }, { $set: { "num_closed_issues": obj.num_closed_issues } });
                                })
                                isChange = true;
                            }
                            if (d.timestamp && d.timestamp !== obj.last_commit && obj.last_commit != 0) {
                                bound(() => {
                                    Examples.update({ _id: d._id }, { $set: { "timestamp": obj.last_commit } });
                                })
                                isChange = true;
                            }

                            if (isChange == true) {
                                let rank_metric = (Math.log(Math.max(1.0, obj.num_stars)) + Math.log(Math.max(1.0, obj.num_forks)) + Math.max(1.0, obj.num_closed_issues - obj.num_open_issues) / Math.max(1.0, obj.num_contributors)) ** (d.timestamp ** (-Math.log(0.9)));
                                if (d.ranking_metric) {
                                    bound(() => {
                                        Examples.update({ _id: d._id }, { $set: { "ranking_metric": rank_metric } });
                                    })
                                }

                                isChange = false;

                            }

                        }


                    });
                }
                // referenced https://stackoverflow.com/questions/65988913/trying-to-get-data-from-python-shell-parsing-it-to-an-object-in-nodejs


            }


        })

    })
}

// let urls = await get_frequent_dataset(2);
// update_database(urls);



