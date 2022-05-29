import { Meteor } from 'meteor/meteor';
import { EJSON } from 'meteor/ejson';
import { Session } from 'meteor/session';
import {PythonShell} from 'python-shell';

export const Examples = new Mongo.Collection('examples');
export const ActionLog = new Mongo.Collection('actionlog');


Meteor.startup(() => {
  //to load new data into the database, run this command:
  //mongoimport --db test --collection <collectionName> --drop --file ~/downloads/<data_dump>.json
  console.log('start-up code running');
  PythonShell.run('/Users/zacyou/Desktop/UCLA/Spring 2022/CS 230/Project/ExamplorePlus/Exampipe/test.py', null, function (err, res) {
            if (err) throw err;
            console.log(res);
  });
  //var reload = true;  
  var reload = true;

  if (reload){
    
    // console.log('reload',reload);
    Assets.getText('findViewById.json', function(err, data) {
      var content = EJSON.parse(data);
      console.log('content',content);
      content.forEach((doc) => {
        doc['codeLength'] = doc['rawCode'].length;
        if (doc['hasTryCatch']===1){
          doc['try'] = 'try {';
        } else {
          doc['try'] = 'empty';
        }
        if (doc['hasFinally']===1){
          doc['finally'] = 'finally {';
        } else {
          doc['finally'] = 'empty';
        }

        if ((doc['guardType']==='IF {') || (doc['guardType']==='IF')){
          doc['guardType'] = 'if ... {';
        } else if ((doc['guardType']==='LOOP {') || (doc['guardType']==='LOOP')){
          doc['guardType'] = 'for/while ... {';
        }

        if ((doc['checkType']==='IF') || (doc['checkType']==='IF {')){
          doc['checkType'] = 'if ... {';
        } else if ((doc['checkType']==='LOOP') || (doc['checkType']==='LOOP {')){
          doc['checkType'] = 'for/while ... {';
        }

        Examples.insert(doc);

      });
      // _.each(content, function(doc){
      
        
      // });
      console.log('how many examples now?',Examples.find().count());

      
          }); 

      
          
  }
});
