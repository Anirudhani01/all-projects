You are a prompt engineer and python architect 
-goal:
i.input :take user story as a input , user provide dynamically 
ii.output:for single test scenario , it should generate all possible multiple test cases
-processing:
i. knowledge base generation:
       -analyse the source code and build knowledge base from the existing source code base (do static analysis -take from existing code and create a domain knowledge out of it ->knowledge base)
ii.then (user story +knowledge )+prompt template -> it should send to llm or gemini api key based on the available 
iii.i will create a prompt_template folder , it should have prompt template 
iv.then user story+ knowledge base(KB) + prompt template -->send to llm or gemini api key for generating test cases
-prompt techinques:
i.graph of through:Map user story -->features -->scenario -->test case
ii.prompt chaining: break process into steps (KB  prompt template  test cases)
iii.few shot prompting:
iv.tree of thorugh:expanding reasoning:
       (story scenario  test steps expected)

-strategies + techiniques:
i.context framing:
     - we don’t just dump user story + kb 
     - we wrap then in a role + instruction prompt
	“you are a QA engineer ,using the user story & the knowledge base ,generate detailed test cases”
ii.knowledge alignment (story + KB merge):
	-user story gives functional requirements 
		“as a user, I want to register so that I can log in later”
	-as knowledge base gives implementation clus
                             for example:
		KB says:register_user() exists ,input field:mail,password
	-when combined ,the llm see both what the feature is supposed to do (story) & how it exist in the code(KB)

iii. Reasoning framework (tree o through /graph of through):
	-LLM internally reson like 
		(user story  features(from KB)  scenario  test cases)
	-examples:
		i.positive:valid email+passwordsuccess
		ii.negative:invalid emailerror
		iii.boundary cases:password length=0 or max length  handled
	-this reasoning path is forced by our instruction(tree of through)
final goal is to generate test cases in textual format ,don’t write the scripts to test case generation
focus on generate for only unit test only exclude functional test ,performace test test ,end to end test and other test
i will provide some test_templates it should select which one is appropriate for this user story and knowledge base
