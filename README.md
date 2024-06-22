# Application Integration Framework for Large Language Model
Large Language Models (LLMs) have opened up new possibilities for processing unstructured information. However, integrating LLMs into traditional applications presents challenges due to their non-deterministic nature. To address this, we introduce a framework designed to effectively integrate LLMs into intermediate modules, ensuring more consistent and reliable outputs.

This framework comprises three essential components: the sieve, the circuit-breaker, and the optimizer. Together, they ensure the LLM produces the desired output and optimize LLM batch processing jobs by minimizing the number of tokens required and the time needed to complete all tasks.

**Demonstration of Framework: Analyse emotion of batch of sentences**

_Please be note that this framework aims to be integrated in different applications. This is just for demonstration, it underscores the potential of the framework for diverse applications._

Experimental results using a structured methodology demonstrate the framework's effectiveness, achieving a 71.05% reduction in processing time and an 82.97% reduction in token usage while maintaining high accuracy.
