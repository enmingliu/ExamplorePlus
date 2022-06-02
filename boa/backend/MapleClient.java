
import edu.iastate.cs.boa.BoaClient;
import edu.iastate.cs.boa.BoaException;
import edu.iastate.cs.boa.CompileStatus;
import edu.iastate.cs.boa.ExecutionStatus;
import edu.iastate.cs.boa.InputHandle;
import edu.iastate.cs.boa.JobHandle;
import edu.iastate.cs.boa.NotLoggedInException;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;


public class MapleClient {
    final String username = "zyou";
    final String password = "Forever";

    public int run(String script, String output_dir, String name) {
        try (final BoaClient client = new BoaClient()) {
            client.login(username, password);

            // print all available input datasets
            InputHandle dataset = client.getDataset("2019 October/GitHub");

            if (dataset == null) {
                System.err.println("Requested Boa dataset does not exist!");
                return -1;
            }

            // submit the query
            JobHandle job = client.query(script, dataset);

            CompileStatus cstatus = job.getCompilerStatus();
            while (cstatus == CompileStatus.RUNNING || cstatus == CompileStatus.WAITING) {
                cstatus = client.getJob(job.getId()).getCompilerStatus();
                // System.out.println("Compilation Status: " + cstatus);
            }

            if (cstatus == CompileStatus.ERROR) {
                System.err.println("Compilation Error!");
                List<String> errors = client.getJob(job.getId()).getCompilerErrors();
                for (String error : errors) {
                    System.err.println(error);
                }
                return -1;
            }

            ExecutionStatus estatus = job.getExecutionStatus();
            while (estatus == ExecutionStatus.RUNNING || estatus == ExecutionStatus.WAITING) {
                estatus = client.getJob(job.getId()).getExecutionStatus();
                // System.out.println("Execution Status: " + estatus);
            }

            if (estatus == ExecutionStatus.ERROR) {
                System.err.println("Execution Error!");
                return -1;
            }

            File oFile = new File(output_dir + "_" + name + ".txt");
            if (oFile.exists()) {
                oFile.delete();
            }
            oFile.createNewFile();

            // dump the output to the given output directory
            job.getOutput(oFile);

            return job.getId();
        } catch (NotLoggedInException e) {
            e.printStackTrace();
        } catch (BoaException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }

        return -1;
    }


    public static void main(String[] args) throws IOException {
        MapleClient client = new MapleClient();

        File dir = new File(
                "./sampleJSON");
        File[] directoryListing = dir.listFiles((directory, name) -> !name.equals(".DS_Store"));

        if (directoryListing != null) {
            for (File child : directoryListing) {
                String content = new String(Files.readAllBytes(Paths.get(
                        "/Users/zacyou/Desktop/UCLA/Spring 2022/CS 230/Project/ExamplorePlus/boa/backend/sampleJSON/"
                                + child.getName())));

                // System.out.println(content);

                ArrayList<String> res = new ArrayList<>(Arrays.asList(content.split(",")));
                String repoURL = "";
                String pathURL = "";

                for (int i = 0; i < res.size(); i++) {
                    if (res.get(i).indexOf("}") > 0) {
                        String temp = res.get(i);
                        res.set(i, temp.replace("}", ""));
                    }

                    if (res.get(i).indexOf("{") > 0) {
                        String temp = res.get(i);
                        res.set(i, temp.replace("{", ""));
                    }

                    // System.out.println(child.getName() + res.get(i));
                    String repo_url = "";
                    String file_url = "";
                    int colonIndex = res.get(i).indexOf(":");
                    int secondColonIndex = res.get(i).indexOf(":", colonIndex + 1);
                    if (res.get(i).length() > secondColonIndex && res.get(i) != null) {

                        repo_url = res.get(i).substring(0, secondColonIndex);
                        file_url = res.get(i).substring(res.get(i).indexOf(":", res.get(i).indexOf(":") + 1) + 1);
                    }

                    pathURL += file_url + ",";
                    repoURL += repo_url + ",";

                }
                pathURL = pathURL.substring(0, pathURL.length() - 1);
                pathURL = pathURL.replace("{", "");
                pathURL = pathURL.replace("}", "");
                repoURL = repoURL.substring(0, repoURL.length() - 1);
                repoURL = repoURL.replace("{", "");
                repoURL = repoURL.replace("}", "");

                String query = "p: Project = input;" +
                        " pj: output collection[string] of time;" +
                        " pj1: output sum[string] of int;" +
                        " q_urls : array of string;" +
                        " q_urls = {" + repoURL + "};" +
                        " q_files: array of string;" +
                        " q_files = {" + pathURL + "};" +
                        " last_commit_date : time;" +
                        " committers: map[string] of bool;" +
                        " getLastSnapshot := function(repo : CodeRepository, file : string) : ChangedFile {" +
                        "  snapshot : ChangedFile;" +
                        "  commit_time : time;" +
                        "  visit(repo, visitor {" +
                        "    before node: Revision -> {" +
                        "      commit_time = node.commit_date; }" +
                        "    before node: ChangedFile -> {" +
                        "      if (node.name != file) stop;" +
                        "      snapshot = node;" +
                        "      last_commit_date  = commit_time;} " +
                        "    }); " +
                        " return snapshot;}; " +
                        " visit(p, visitor { " +
                        "  before node: CodeRepository -> {" +
                        "    foreach(i:int; def(q_urls[i])) {" +
                        "      q_url := q_urls[i];" +
                        "      if(p.project_url == q_url) {" +
                        "        q_file := q_files[i];" +
                        "        snapshot := getLastSnapshot(node, q_file);" +
                        "        pj[q_url+\"/tree/master/\"+q_file] << last_commit_date;" +
                        "        foreach (j: int; def(p.code_repositories[j]))" +
                        "         foreach (z: int; def(p.code_repositories[j].revisions[z])) " +
                        "          committers[p.code_repositories[j].revisions[z].committer.username] = true;" +
                        "        if (len(committers) > 0)pj1[q_url+\"/tree/master/\"+q_file] << len(committers); }}stop;}});";

                client.run(query,
                        "/Users/zacyou/Desktop/UCLA/Spring 2022/CS 230/Project/ExamplorePlus/boa/output",
                        child.getName());

            }

        } else {
            System.out.print("file not existed");
        }

    }
}