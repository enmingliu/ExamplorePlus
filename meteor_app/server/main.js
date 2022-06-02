
import { Meteor } from 'meteor/meteor';
import { EJSON } from 'meteor/ejson';
import { CronJob } from 'cron';
import { get_frequent_dataset, update_database } from './checkFreq';


export const Examples = new Mongo.Collection('examples');
export const ActionLog = new Mongo.Collection('actionlog');


Meteor.startup(() => {
  //to load new data into the database, run this command:
  //mongoimport --db test --collection <collectionName> --drop --file ~/downloads/<data_dump>.json

  //var reload = true;  
  var reload = false;

  if (reload){
    
    // console.log('reload',reload);
    Assets.getText('addView.json', function(err, data) {
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

  //referenced https://stackoverflow.com/questions/40687237/cron-jobs-in-meteor
  new CronJob({
    cronTime: '0 8 * * *', // everyday at 8 am
    onTick: Meteor.bindEnvironment(async () => {
      let x = 0, Y=0;

      // console.log("=======================================before======================================================")

      // Examples.find().forEach(d => {
      //   if(Y < 3){
      //     console.log(d);
      //     Y++;
      //   }
      // })

      // console.log("===================================================================================================")

      let urls = await get_frequent_dataset();
      if(urls && urls.length > 0){
        update_database(urls);
      }
      // console.log("=======================================after======================================================")

      // Examples.find().forEach(d => {
      //   if(x < 3){
      //     console.log(d);
      //     x++;
      //   }
      // })
      // console.log("===================================================================================================")

    }),
    start: true,
    timeZone: 'America/Los_Angeles',
  });
});

