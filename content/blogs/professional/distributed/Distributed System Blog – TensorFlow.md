---
aliases:
  - /professional/distributed/distributed-system-blog--tensorflow/
---

### Part 1: Goal Statement of TensorFlow

The goal of this paper is to design a general machine learning computational framework, which is able to support different models and algorithms flexibly and support distributed computation on various and large-scale heterogeneous hardware (such as CPU, GPU, TPU; single-machine, multi-machine). It aimed to solve the problems of previous ML framework (like DistBelief): low flexibility, low automation and extensibility due to the layer-based design. For example, in TensorFlow, users do not need to handle backpropagation, distributed communication, and hardware details, the framework automatically supports these features as long as the dataflow graph has been defined.

### Part 2: Side View of TensorFlow

I think the essence of TensorFlow is also the core of computer science–abstraction, specifically the separation of declaration and execution. In TensorFlow, users declare the dataflow graph of the model. The framework then optimizes and decides how to execute. This decoupling means the two sides can evolve independently: the same graph can run on a single GPU today and a cluster of TPUs tomorrow, without changing a single line of user code. This pattern appears throughout computer science. SQL works the same way: users declare what data they want, and the database engine decides how to retrieve it. The separation of declaration and execution makes the development much clearer and makes upper-level declarations easily reusable across different environments.