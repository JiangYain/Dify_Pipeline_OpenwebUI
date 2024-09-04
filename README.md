# Dify_Pipeline_OpenwebUI

通过该项目将Dify通过Pipeline接入OpenwebUI，可以兼并OpenwebUI的前端优势和相应生态以及Dify强大的模型可拓展性和Workflow的效益。

By integrating Dify into OpenwebUI through the Pipeline, this project aims to combine the front-end advantages and ecosystem of OpenwebUI with the powerful model scalability and workflow benefits of Dify.

### 2023-08-15
08.15 初步测试没有遇到问题 

The initial test on 08.15 did not encounter any issues.

### 2023-08-19
08.19 很遗憾，当前前端似乎没有办法正确的在pipe中传入chat_id，而Dify的conversation_id是自动生成的。我们没法很好的建立两者的映射关系，因为Chat_id并不存在于Pipe方法传入的参数内，并且 chat_id 并不由"新建会话"生成，而是会话界面发送了任意一条信息后生成的。这会导致不同会话的上下文没有办法保持独立。

On 08.19, unfortunately, the current front-end seems unable to correctly pass `chat_id` into the pipeline, and Dify's `conversation_id` is automatically generated. We can't establish a proper mapping between the two because `chat_id` is not included in the parameters passed to the pipeline method, and `chat_id` is not generated by "create a new session" but is instead generated after any message is sent from the session interface. This results in the context of different sessions being unable to remain independent.

### 2023-08-20
08.20 参照OUI的某个issue进行重构，对Pipeline类做了以下改动：

On 08.20, following a reference to a specific issue in OUI, the Pipeline class was refactored with the following changes:

1. 在`__init__`方法中，我们添加了`self.chat_id = None`来初始化chat_id 

   In the `__init__` method, we added `self.chat_id = None` to initialize `chat_id`.

2. 添加了`inlet`方法，用于存储从body中获取的chat_id 

   Added the `inlet` method to store the `chat_id` retrieved from the body.

3. 在`pipe`方法中，我们现在使用`self.chat_id`而不是从body中获取chat_id 

   In the `pipe` method, we now use `self.chat_id` instead of retrieving `chat_id` from the body.

4. 在处理conversation_id时，我们同样使用`self.chat_id` 

   When handling `conversation_id`, we also use `self.chat_id`.

5. 在`_handle_streaming_response`和`_handle_blocking_response`方法中，我们也使用`self.chat_id`来存储和检索conversation_id 

   In the `_handle_streaming_response` and `_handle_blocking_response` methods, we also use `self.chat_id` to store and retrieve `conversation_id`.

这样的话，现在chat_id是在类的实例变量中存储的，而不是每次都从body中获取。测试下来好像没有问题，但是这种方法在并发访问时一定会有问题。后面再改吧

In this way, `chat_id` is now stored as an instance variable in the class instead of being retrieved from the body each time. Testing seems to show no issues, but this method will likely have problems with concurrent access. I'll revisit it later.

### 2023-09-04
9.04 我创建了一个新的Demo，因为原先的Pipeline在生成侧边栏标题的时候会因为输出格式不符合OpenAI规范而留空白 如果在OUI中使用同一个Pipeline 会产生很高的负载 可以分出两条Pipeline来处理"标题生成"以及"对话" 

On 09.04, I created a new demo because the original `Pipeline` would leave the sidebar title blank due to the output format not meeting OpenAI's standards. If the same `Pipeline` is used in OUI, it can generate a high load. It's possible to separate the pipeline into two: one for "title generation" and another for "dialogue."
