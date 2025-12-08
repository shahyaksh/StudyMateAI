// Lecture data for the course - Lectures 7 and 10
// This file contains transcript data, descriptions, and notes

export interface TranscriptItem {
  time: string
  text: string
}

// Lecture 7 Transcript Data
export const lecture7TranscriptData: TranscriptItem[] = [
  { time: '00:00 - 01:00', text: 'Okay, so today we\'ll start talking about the larger models, starting from GPT-3. Now that we covered the pre-trained models like GPT-2 and BERT, we focus more on the larger models and we\'ll see some unique abilities they have.' },
  { time: '01:00 - 02:00', text: 'Basically, the main architecture is still the Transformer; there is no significant change in the structure of these models. They are just much bigger and are trained on massive datasets.' },
  { time: '02:00 - 03:00', text: 'The training becomes much more complicated—it\'s not something you can do in a few days like BERT; it takes months and huge engineering challenges involving hundreds of people. It also requires a lot of resources in terms of costs, GPUs, and computation time.' },
  { time: '03:00 - 04:00', text: 'In addition to the size, these models exhibit special abilities that we call emergent abilities. These are abilities that were not explicitly programmed in the code.' },
  { time: '04:00 - 05:00', text: 'Because these models are trained for next-word prediction, but because they are so huge and trained on a lot of data, they are able to perform tasks that are not necessarily NLP-focused. Examples include reasoning tasks, math problems, instruction following, using tools like a web browser, or even self-evaluation.' },
  { time: '05:00 - 06:00', text: 'This is quite remarkable because no one initially expected these models to have these abilities; we simply expected them to become better on NLP tasks. *Student Question: At what point do you say that a model is "large"?*' },
  { time: '06:00 - 07:00', text: 'There is no clear definition. Mostly people say about 10 billion parameters. For example, GPT-2 is still not considered large (1.5B), but usually, these models are at least 10 billion.' },
  { time: '07:00 - 08:00', text: 'LLaMA is relatively small (70B is the largest version), but it is considered an LLM because it can achieve performance quite close to GPT-3 or 4.' },
  { time: '08:00 - 09:00', text: 'However, size is not the only factor; the amount of data used for training is also important. This domain is very dynamic, so LLMs are changing very fast. Here are the top leading LLMs: The top ones are usually closed source.' },
  { time: '09:00 - 10:00', text: 'This includes GPT-5 (OpenAI), Claude (Anthropic)—which is leading in safety scores—and Gemini (Google). On the open-source side, we have LLaMA (Meta), Mistral, Grok, and DeepSeek. DeepSeek is open source and they publish all the details of the training.' },
  { time: '10:00 - 11:00', text: 'For example, they use a Mixture of Experts (MoE) architecture with 671 billion parameters, but only 37 billion are activated in each prediction. DeepSeek is also notable for being very cheap to train (only $6 million).' },
  { time: '11:00 - 12:00', text: '*Student Discussion regarding DeepSeek:* There are concerns about using DeepSeek with private data because it comes from China, and there are laws regarding data sharing with the government.' },
  { time: '12:00 - 13:00', text: 'However, since they publish the code and training algorithm, you can theoretically train a new model yourself if you have the budget.' },
  { time: '13:00 - 14:00', text: 'Before we discuss these models in detail, there is an important observation from 2020 called Scaling Laws. These are simple power laws that govern the relationship between a model\'s performance and its size, dataset size, and compute budget.' },
  { time: '14:00 - 15:00', text: 'They allow us to predict the performance of larger models based on smaller ones without training a new model every time.' },
  { time: '15:00 - 16:00', text: 'The laws consider three main variables: Model Size ($N$) (excluding embeddings), Dataset Size ($D$), and Compute Budget ($C$), measured in PF-days. The first paper introducing this was "Scaling Laws for Neural Language Models" by Kaplan et al. (OpenAI).' },
  { time: '16:00 - 17:00', text: 'They analyzed the test loss against these variables using a logarithmic scale. On a log-log plot, the relationship appears as a straight line, which indicates a power law ($y = ax^k$).' },
  { time: '17:00 - 18:00', text: 'Key conclusions included that we can get better results by simply increasing the size without changing the architecture, but there are diminishing returns—as the model gets larger, it becomes harder to improve performance.' },
  { time: '18:00 - 19:00', text: 'They also noted that overfitting occurs if you increase the model size or dataset size while holding the other fixed, and that convergence is inefficient; it is better to invest the compute budget in increasing the model size or data rather than training to full convergence.' },
  { time: '19:00 - 20:00', text: 'Motivated by this research, OpenAI created GPT-3 in 2020. They scaled the model from 1.5B (GPT-2) to 175B parameters and trained it on 300 billion tokens.' },
  { time: '20:00 - 21:00', text: 'The architecture was the same as GPT-2 (Transformer decoder), but with a larger context size (2048 tokens). One innovation in GPT-3 was the use of Sparse Attention.' },
  { time: '21:00 - 22:00', text: 'In a standard Transformer, the attention matrix is $N^2$ (quadratic complexity), which is a bottleneck for memory and computation. Sparse attention reduces this by having tokens attend only to a subset of other tokens, reducing complexity to $O(n\\sqrt{n})$.' },
  { time: '22:00 - 23:00', text: 'This allowed them to scale to nearly 100 layers. GPT-3 used a mix of datasets. 60% of the training mix came from Common Crawl (filtered web data), but they also included high-quality datasets like WebText2, Books1, Books2, and Wikipedia.' },
  { time: '23:00 - 24:00', text: 'Mixing high-quality data (like books) with web data is crucial because web data is noisy and often short, whereas books provide long, coherent stories essential for learning long-range dependencies.' },
  { time: '24:00 - 25:00', text: 'A major discovery with GPT-3 was In-Context Learning (ICL). Even after pre-training is finished, the model can learn to perform new tasks just from the prompt, without updating any weights (no gradient updates).' },
  { time: '25:00 - 26:00', text: 'We define three settings: Zero-shot (task description only), One-shot (description plus one example), and Few-shot (description plus multiple examples). Experimental results showed that only the largest models (175B) benefit significantly from in-context learning.' },
  { time: '26:00 - 27:00', text: 'Smaller models do not show this "emergent" ability. In the few-shot setting, GPT-3 outperformed a fine-tuned BERT Large on the SuperGLUE benchmark.' },
  { time: '27:00 - 28:00', text: 'Despite its success, GPT-3 has limitations. It lacks consistency (can provide different answers to the same question), loses coherence over long passages, reflects biases present in the training data, and its performance is heavily dependent on how the prompt is formatted—leading to the field of Prompt Engineering.' },
  { time: '28:00 - 29:00', text: 'As models got better, benchmarks like GLUE became too easy. New benchmarks were created, such as MMLU (Massive Multitask Language Understanding). MMLU covers 57 subjects (math, physics, law, humanities) with roughly 15,000 multiple-choice questions. Human expert accuracy is around 90%.' },
  { time: '29:00 - 30:00', text: 'GPT-4 achieves around 87%, and Gemini Ultra achieved roughly 90%. Because models were saturating MMLU, MMLU-Pro was created. It filters simple questions, adds complex reasoning, and increases options from 4 to 10 to reduce random guessing probability.' },
  { time: '30:00 - 31:00', text: 'Next time, we will discuss the Chinchilla Scaling Laws, which corrected Kaplan\'s laws regarding data sizing, and the lifecycle of LLMs (pre-training, fine-tuning, RLHF). We also have the midterm exam coming up.' }
]

export const lecture7Description = `Today we'll start talking about the larger models, starting from GPT-3. Now that we covered the pre-trained models like GPT-2 and BERT, we focus more on the larger models and we'll see some unique abilities they have. The main architecture is still the Transformer; there is no significant change in the structure of these models. They are just much bigger and are trained on massive datasets.`

export const lecture7Notes = `Key Topics Covered:
- Introduction to Large Language Models (LLMs)
- GPT-3 architecture and scaling
- Emergent abilities in large models
- Definition of "large" models (10B+ parameters)
- Leading LLMs: GPT-5, Claude, Gemini, LLaMA, Mistral, DeepSeek
- Mixture of Experts (MoE) architecture
- Scaling Laws (Kaplan et al., 2020)
- Model Size, Dataset Size, and Compute Budget relationships
- GPT-3: 175B parameters, 300B tokens
- Sparse Attention mechanism
- Training data composition (Common Crawl, WebText2, Books, Wikipedia)
- In-Context Learning (ICL): Zero-shot, One-shot, Few-shot
- GPT-3 limitations and Prompt Engineering
- Benchmarks: GLUE, SuperGLUE, MMLU, MMLU-Pro`

// Lecture 10 Transcript Data (same as lecture 7 content - appears to be duplicate)
export const lecture10TranscriptData: TranscriptItem[] = lecture7TranscriptData

export const lecture10Description = lecture7Description

export const lecture10Notes = lecture7Notes

// Video URLs
export const lecture7VideoUrl = '/video/Lecture-7.mp4'
export const lecture10VideoUrl = '/video/Lecture-10.mp4'
