"""
Generates 5-part mini-series entries for the 20 GOAT AI Papers (100 total videos)
and safely appends them to data/topic_queue.json without duplicates.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOPIC_QUEUE_FILE = PROJECT_ROOT / "data" / "topic_queue.json"

GOAT_PAPERS = [
    # 1. Attention Is All You Need
    ("1706.03762", "Attention Is All You Need", "transformer", [
        ("The Death of Recurrence: Why LSTMs Hit the Parallelism Wall", "architecture_breakdown", "Why sequential token passing throttled GPU parallelism, and how self-attention unlocked simultaneous matrix computation across entire documents."),
        ("The Scaled Dot-Product Engine: Mathematical Derivation of QK^T / sqrt(d_k)", "mechanism_deepdive", "Why the square root scaling factor prevents softmax gradient collapse into barren regions in high dimensional embedding spaces."),
        ("Multi-Head Projection: Subspace Geometry and Positional Frequency Encodings", "mechanism_deepdive", "How multi-head linear projections split representations into orthogonal semantic subspaces, and why sinusoidal frequencies encode relative order."),
        ("The 28.4 BLEU Translation Shockwave That Shattered Academic Benchmarks", "benchmark_news", "How the 8-layer base and 65-million parameter big Transformer crushed WMT English-to-German and English-to-French translation records in 2017."),
        ("The Universal Architecture: How One Paper Birthed GPT, Claude, Gemini, and Modern AI", "architecture_breakdown", "How the identical attention building block scaled across text, vision, protein folding, audio, and robotics over seven years.")
    ]),
    # 2. ResNet
    ("1512.03385", "ResNet: Deep Residual Learning", "resnet", [
        ("The Degradation Paradox: Why Deeper Networks Became Stupider", "architecture_breakdown", "The counter-intuitive discovery that deeper vanilla networks had higher training error than shallow ones, and why vanishing gradients were the culprit."),
        ("The Superconducting Gradient Wire: Mathematical Anatomy of F(x) + x", "mechanism_deepdive", "How identity shortcut skip connections allow gradient vectors to propagate backward across hundreds of layers without attenuation."),
        ("The 152-Layer Architecture: Bottleneck Residual Blocks and Dimension Projections", "mechanism_deepdive", "Designing 1x1, 3x3, and 1x1 bottleneck layers to drastically reduce parameter count while scaling layer depth to unprecedented heights."),
        ("Crushing ImageNet 2015: 3.57% Error Rate and 5 Clean Sweep Competitions", "benchmark_news", "How ResNet crushed human-level vision performance on ImageNet classification, localization, detection, and COCO benchmarks."),
        ("The Indestructible Skeleton: Why Every Modern Transformer Still Relies on Residual Connections", "architecture_breakdown", "How the residual stream remains the primary communication bus inside modern LLMs from GPT-4 to Llama 3.")
    ]),
    # 3. AlexNet
    ("alexnet_imagenet_2012", "AlexNet: Deep Learning Ignition", "alexnet", [
        ("The Great Vision Schism: Handcrafted SIFT Features vs Raw Pixel Learning", "architecture_breakdown", "Why the computer vision community resisted neural networks for decades until raw pixel convolutions proved handcrafted features obsolete."),
        ("The 3 Pillars of Modern AI: GPUs, ReLU Activations, and Dropout Regularization", "mechanism_deepdive", "Replacing slow Sigmoid with piecewise linear ReLU to defeat vanishing gradients, paired with random node dropout to prevent co-adaptation."),
        ("The Dual-GTX-580 Split Pipeline: Model Parallelism Before It Had a Name", "mechanism_deepdive", "How Alex Krizhevsky split 60 million parameters across two 3GB gaming GPUs using cross-GPU communication layers."),
        ("The 15.3% Shock: How AlexNet Demolished ImageNet and Changed History", "benchmark_news", "The dramatic moment at ECCV 2012 when AlexNet outperformed the second-place handcrafted model by an unthinkable 10.8 percentage points."),
        ("The Deep Learning Big Bang: How Three Researchers Sparked the Trillion-Dollar AI Boom", "architecture_breakdown", "How AlexNet triggered the worldwide pivot of Google, Facebook, Microsoft, and academic labs into deep neural networks.")
    ]),
    # 4. GPT-3
    ("2005.14165", "GPT-3: Few-Shot In-Context Learners", "gpt3", [
        ("The Death of Fine-Tuning: Moving from Weight Updates to Natural Language Prompts", "architecture_breakdown", "Why training separate fine-tuned heads per task was obsolete, and how scaling models turned English into a universal programming language."),
        ("The Geometry of In-Context Learning: How Frozen Weights Simulate Gradient Descent", "mechanism_deepdive", "The mathematical phenomenon where few-shot prompt tokens act as steering vectors that navigate latent manifolds without weight updates."),
        ("The 175-Billion Parameter Monster: Megatron Tensor Slicing and Sparse Alternation", "mechanism_deepdive", "The engineering breakthrough of training 175B parameters across thousands of V100 GPUs using Megatron-style tensor and pipeline parallelism."),
        ("The Few-Shot Benchmark Surge: TriviaQA, LAMBADA, Arithmetic, and Real-Time Translation", "benchmark_news", "Systematic evaluation demonstrating that few-shot performance scales steadily across dozens of diverse linguistic benchmarks."),
        ("The Emergence Horizon: How Scale Discovered Abilities No Human Programmed", "architecture_breakdown", "How scaling autoregressive next-token prediction induced qualitative phase transitions in reasoning, code generation, and translation.")
    ]),
    # 5. AlphaGo & AlphaZero
    ("alphago_nature_2016", "AlphaGo: Mastering the Game of Go", "alphago", [
        ("The 10^170 Complexity Trap: Why Classical Brute-Force Search Was Dead in Go", "architecture_breakdown", "Why the game of Go has more legal board states than atoms in the universe, making traditional minimax search impossible."),
        ("Policy vs Value Networks: Fusing Grandmaster Intuition with Cold Calculation", "mechanism_deepdive", "How policy networks prune the search space to high-probability moves while value networks evaluate board position without exhaustive rollouts."),
        ("Monte Carlo Tree Search Integration: Upper Confidence Bounds and Neural Rollouts", "mechanism_deepdive", "Balancing exploration and exploitation using PUCT equations to guide dynamic tree expansion toward winning branches."),
        ("Move 37: The Moment an Algorithm Played a Move No Human Had Seen in 3,000 Years", "benchmark_news", "Analyzing Move 37 in Game 2 against Lee Sedol: how a 1-in-10,000 probability move redefined human understanding of Go strategy."),
        ("From Expert Bootstrapping to Pure Self-Play: The AlphaZero Legacy", "architecture_breakdown", "How AlphaGo evolved into AlphaZero and MuZero, discovering superhuman strategies in chess, shogi, and Go entirely from scratch.")
    ]),
    # 6. GANs
    ("1406.2661", "GANs: Generative Adversarial Networks", "gans", [
        ("The Counterfeiter and the Cop: Zero-Sum Game Theory in Deep Learning", "architecture_breakdown", "Formulating generative AI as a minimax game between a Generator forging fake data and a Discriminator detecting authentic samples."),
        ("The Minimax Equation: Mathematical Proof of Jensen-Shannon Divergence Convergence", "mechanism_deepdive", "The theoretical derivation proving that the optimal discriminator is D*(x) = p_data / (p_data + p_g), leading to global minimum p_g = p_data."),
        ("Mode Collapse and Vanishing Gradients: Why Training Early GANs Was Like Walking a Tightrope", "mechanism_deepdive", "Analyzing failure modes where generators memorize single sample clusters or discriminators overpower generators with zero gradient signals."),
        ("The Photorealism Revolution: From 28x28 MNIST Blobs to High-Res Face Synthesis", "benchmark_news", "The progression through DCGAN, WGAN, and StyleGAN that produced faces indistinguishable from real human photographs."),
        ("The Generative Legacy: How Adversarial Modeling Paved the Way for Modern Diffusion", "architecture_breakdown", "How GAN latent space interpolation, perceptual loss, and adversarial discriminators laid the groundwork for modern media synthesis.")
    ]),
    # 7. DDPM
    ("2006.11239", "DDPM: Denoising Diffusion Probabilistic Models", "ddpm", [
        ("Statistical Thermodynamics in AI: Turning Non-Equilibrium Physics into Generative Art", "architecture_breakdown", "Why reversing physical entropy and noise diffusion fundamentally outperforms adversarial min-max games for stable image synthesis."),
        ("The Forward-Reverse Markov Chain: Reparameterization Trick and Closed-Form Noise Addition", "mechanism_deepdive", "The mathematical magic of sampling noisy image x_t directly from x_0 at any arbitrary timestep using Gaussian schedules without step-by-step iteration."),
        ("The Denoising U-Net: Time-Step Embeddings, Skip Connections, and Score Matching", "mechanism_deepdive", "How a U-Net architecture predicts the exact noise vector epsilon added to each pixel rather than predicting the clean image directly."),
        ("Toppling GANs on ImageNet: Lower FID Scores and True Distribution Coverage", "benchmark_news", "The landmark empirical demonstration that diffusion models achieve superior Fréchet Inception Distance without mode collapse."),
        ("The Latent Diffusion Explosion: How DDPM Formed the Foundation of Stable Diffusion, Midjourney and Sora", "architecture_breakdown", "How compressing pixel diffusion into latent space via VAEs enabled real-time high-definition video and image generation worldwide.")
    ]),
    # 8. InstructGPT
    ("2203.02155", "InstructGPT: RLHF Alignment", "instructgpt", [
        ("The Alignment Gap: Why Pure Next-Token Autocomplete Was Dangerous and Toxic", "architecture_breakdown", "Why standard language models prioritize internet frequency over human truthfulness, frequently generating offensive, biased, or evasive outputs."),
        ("The Bradley-Terry Reward Engine: Converting Human Pairwise Preferences into Scalar Loss", "mechanism_deepdive", "The mathematical formulation training a reward model to score responses based on human thumbs-up comparisons using sigmoid cross-entropy."),
        ("PPO Policy Optimization: Balancing Human Rewards with KL-Divergence Anchors", "mechanism_deepdive", "How Proximal Policy Optimization steers model weights toward high reward while a KL-divergence penalty prevents policy collapse into gibberish."),
        ("The 1.3B Beats 175B Miracle: How Alignment Trumped 100x Parameter Scale", "benchmark_news", "The empirical benchmark proving that a 1.3-billion parameter InstructGPT model was rated vastly superior to a 175-billion unaligned GPT-3."),
        ("The ChatGPT Ignition: The Single Paper That Brought AI to 100 Million Consumers", "architecture_breakdown", "How the 3-stage alignment blueprint (SFT -> Reward Model -> PPO) unlocked conversational AI and catalyzed modern LLM products.")
    ]),
    # 9. Scaling Laws
    ("2001.08361", "Scaling Laws for Neural Language Models", "scaling_laws", [
        ("From Trial-and-Error to Predictable Physics: The Discovery of Neural Power Laws", "architecture_breakdown", "How researchers discovered that model loss decreases smoothly as a power-law function of compute, data, and parameters over orders of magnitude."),
        ("The Triad Exponents: Compute (C), Parameters (N), and Dataset Size (D)", "mechanism_deepdive", "The mathematical derivation of power-law exponents alpha_N, alpha_D, and alpha_C, proving that network depth vs width matters far less than raw scale."),
        ("The Overfitting Mirage: Why Larger Models Are Always More Sample-Efficient", "mechanism_deepdive", "Proving mathematically that bigger models achieve lower cross-entropy loss with fewer training tokens and fewer optimization steps than smaller models."),
        ("Predicting Frontier Performance Across 4 Orders of Magnitude: The Billion-Dollar Graph", "benchmark_news", "How small-scale compute runs accurately predicted the exact performance curves of multi-thousand GPU clusters months before training completed."),
        ("The Capital Supercycle: How One Empirical Paper Justified the Trillion-Dollar Data Center Boom", "architecture_breakdown", "How the scaling law equations gave cloud providers and venture capital the mathematical confidence to invest hundreds of billions into AI hardware.")
    ]),
    # 10. FlashAttention
    ("2205.14135", "FlashAttention: Fast & Memory-Efficient Exact Attention", "flashattention", [
        ("The Memory Wall: Why Modern GPUs Were Idling While Computing Attention", "architecture_breakdown", "Why standard attention was memory-bandwidth bound rather than compute bound, leaving high-performance tensor cores starved of data."),
        ("IO-Aware Hardware Tiling: Bypassing Slow HBM by Exploiting 20 TB/s On-Chip SRAM", "mechanism_deepdive", "Re-engineering transformer attention to load matrix blocks into ultra-fast SRAM tiles, computing intermediate values without spilling to slow HBM memory."),
        ("The Online Softmax Breakthrough: Exact Normalization Without Storing N x N Matrices", "mechanism_deepdive", "The clever mathematical reformulation of the softmax normalization constant that allows exact attention output accumulation across incremental tiles."),
        ("The 4x Speedup: Slashing Training Time and Unlocking 64K to 1M Context Windows", "benchmark_news", "Benchmarking FlashAttention across BERT, GPT-2, and long-sequence models, proving 2-4x end-to-end wall-clock speedups with zero loss in mathematical precision."),
        ("The Universal Hardware Standard: How FlashAttention Rewrote Every Frontier AI Kernel", "architecture_breakdown", "How FlashAttention-2 and FlashAttention-3 became the mandatory low-level execution engine across PyTorch, vLLM, DeepSeek, and modern LLM serving.")
    ]),
    # 11. Word2Vec
    ("1301.3781", "Word2Vec: Semantic Vector Spaces", "word2vec", [
        ("The Curse of Discrete Tokens: Why Early NLP Treated Dog and Cat as Orthogonal", "architecture_breakdown", "Why 50,000-dimensional sparse one-hot encodings failed to capture synonymy or semantic similarity, and the need for dense continuous embeddings."),
        ("Skip-Gram with Negative Sampling: Turning Text Co-Occurrence into Logistic Dot Products", "mechanism_deepdive", "The efficient neural objective maximizing dot products of observed word-context pairs while pushing away random negative noise words."),
        ("Distributed Vector Algebra: The Magic of King - Man + Woman = Queen", "mechanism_deepdive", "How linear vector offsets in a 300-dimensional space encode abstract semantic, syntactic, and relational concepts without explicit supervision."),
        ("Crushing Word Analogy Benchmarks: Semantic and Syntactic Accuracy Milestones", "benchmark_news", "Evaluating Word2Vec on thousands of complex semantic and grammatical analogies, setting historical state-of-the-art benchmarks in 2013."),
        ("The Vector Database Genesis: How Word2Vec Built the Foundation for Dense Retrieval and RAG", "architecture_breakdown", "Tracing the lineage from Word2Vec through GloVe and Sentence-Transformers to modern dense vector search and RAG retrieval systems.")
    ]),
    # 12. DQN
    ("1312.5602", "Deep Q-Networks (DQN): Deep Reinforcement Learning", "dqn", [
        ("The High-Dimensional RL Barrier: Why Reinforcement Learning Failed on Video Games", "architecture_breakdown", "Why classical reinforcement learning relied on hand-crafted state features and collapsed when confronted with continuous 210x160 pixel screens."),
        ("The Bellman Loss Equation: Approximating High-Dimensional Action-Value Functions", "mechanism_deepdive", "Formulating deep Q-learning where a convolutional neural network directly maps raw RGB frames to expected discounted future rewards Q(s, a)."),
        ("Experience Replay and Target Networks: Taming Deadly Feedback Instabilities", "mechanism_deepdive", "How randomizing historical transitions from an experience replay buffer breaks temporal correlation, and fixed target weights prevent runaway divergence."),
        ("The Atari Breakout Tunnel: When an Artificial Agent Discovered Long-Term Strategy", "benchmark_news", "The historic moment when DQN autonomously discovered the strategy of digging a tunnel through the side wall to bounce the ball endlessly behind the blocks."),
        ("The Deep RL Revolution: From 8-Bit Cartridges to Robotics and Autonomous Systems", "architecture_breakdown", "How DQN sparked modern Deep RL, leading directly to AlphaGo, robotic manipulation, and reinforcement learning alignment for frontier LLMs.")
    ]),
    # 13. BERT
    ("1810.04805", "BERT: Deep Bidirectional Transformers", "bert", [
        ("The Unidirectional Trap: Why Autoregressive Models Missed Half the Sentence Context", "architecture_breakdown", "Why left-to-right language models like GPT-1 could not incorporate future context into current representations, crippling performance on classification and QA."),
        ("Masked Language Modeling: The 15% Cloze Task That Unlocked Deep Bidirectional Context", "mechanism_deepdive", "The mathematical design behind replacing 15% of tokens with [MASK] or random words, forcing the Transformer encoder to attend to both left and right context simultaneously."),
        ("Next Sentence Prediction & Cross-Attention: Teaching Transformers Inter-Sentence Cohesion", "mechanism_deepdive", "Training multi-task objectives on sentence pair relationships [CLS] A [SEP] B [SEP] to power complex reading comprehension and semantic entailment."),
        ("The GLUE Benchmark Decimation: Shattering State-of-the-Art on 11 NLP Tasks in One Shot", "benchmark_news", "How BERT-Base and BERT-Large swept SQuAD, MultiNLI, and GLUE leaderboards, outperforming human baselines on several language benchmarks."),
        ("The Search Engine Transformation: How BERT Rewrote the Architecture of Google Search", "architecture_breakdown", "How Google integrated BERT into its core search ranking algorithm to understand conversational, multi-word queries for billions of daily users.")
    ]),
    # 14. ViT
    ("2010.11929", "Vision Transformer (ViT): Attention for Visual Recognition", "vit", [
        ("The Inductive Bias Myth: Do We Actually Need Convolutions for Computer Vision?", "architecture_breakdown", "Questioning the dogma of translation invariance and local connectivity, asking if a pure Transformer could learn visual geometry from data alone."),
        ("An Image is Worth 16x16 Words: Flattening Pixel Patches into Standard Transformer Tokens", "mechanism_deepdive", "The elegant mathematical projection chopping 2D images into 16x16 pixel patches, flattening them into 1D vectors, and prepending a learnable [CLS] token."),
        ("Global Self-Attention Across Pixels: Why Patch Mixing Beats Local Receptive Fields", "mechanism_deepdive", "How self-attention allows early visual layers to integrate context from opposite corners of the image instantly, unlike CNNs that expand slowly across layers."),
        ("The JFT-300M Scaling Breakthrough: When Transformers Surpassed CNNs at Massive Scale", "benchmark_news", "Proving that while CNNs win on small datasets, ViT systematically outperforms SOTA ResNets and EfficientNets when pre-trained on hundreds of millions of images."),
        ("The Multimodal Unification: How ViT Collapsed NLP and Computer Vision into One Architecture", "architecture_breakdown", "How ViT eliminated specialized vision backbones, paving the way for unified multimodal models (CLIP, Flamingo, GPT-4V, Gemini).")
    ]),
    # 15. CLIP
    ("2103.00020", "CLIP: Contrastive Language-Image Pretraining", "clip", [
        ("The Closed-World Trap: Why 1,000 Fixed ImageNet Labels Stunted Computer Vision", "architecture_breakdown", "Why training models to classify images into rigid category labels prevented zero-shot generalization to real-world visual concepts."),
        ("Contrastive Dual-Encoder Alignment: Maximizing Diagonal Dot-Products in Shared Latent Space", "mechanism_deepdive", "The symmetric cross-entropy loss aligning N image embeddings with N text embeddings across an N x N similarity matrix with learnable temperature tau."),
        ("Zero-Shot Visual Inference: Classifying Any Object by Prompting Text Encoders", "mechanism_deepdive", "How prompting the text encoder with 'a photo of a {label}' allows instant visual classification across thousands of unseen categories without fine-tuning."),
        ("The Adversarial Robustness Shield: Outperforming ResNet-50 on Real-World Distribution Shifts", "benchmark_news", "Demonstrating that CLIP matches ImageNet accuracy while performing radically better on sketches, ObjectNet, ImageNet-R, and adversarial perturbations."),
        ("The Text-to-Image Steering Wheel: The Guiding Engine Behind DALL-E, Stable Diffusion and Midjourney", "architecture_breakdown", "How CLIP cosine similarity embeddings served as the foundational guidance mechanism that steered early diffusion models toward user prompts.")
    ]),
    # 16. AlphaFold 2
    ("alphafold2_nature_2021", "AlphaFold 2: The Protein Folding Revolution", "alphafold2", [
        ("The 50-Year Biological Enigma: Why Predicting 3D Protein Folding Was Thought Impossible", "architecture_breakdown", "The grand challenge of molecular biology: deciphering how a 1D sequence of amino acids folds into complex 3D functional structures in microseconds."),
        ("The Evoformer Engine: Dual-Attention Over Multiple Sequence Alignments and Pair Representations", "mechanism_deepdive", "How the Evoformer processes evolutionary co-variation across species while updating 2D residue-residue distance matrices in tandem."),
        ("SE(3)-Equivariant Structure Module: Predicting 3D Rigid Rotations and Backbone Torsions", "mechanism_deepdive", "Operating directly on 3D Euclidean coordinates using rotation matrices and invariant point attention to fold proteins with atomic precision."),
        ("CASP14 Decimation: Sub-Angstrom GDT Accuracy That Stunned the Global Scientific Community", "benchmark_news", "The historic moment at the CASP14 competition when AlphaFold 2 achieved an average score of 92.4 GDT, matching experimental X-ray crystallography accuracy."),
        ("The Nobel Prize in Chemistry: Mapping 200 Million Known Proteins to Transform Medicine", "architecture_breakdown", "How DeepMind open-sourced the 3D structures of virtually all known proteins, accelerating structural biology, drug design, and enzyme engineering.")
    ]),
    # 17. LoRA
    ("2106.09685", "LoRA: Low-Rank Adaptation of Large Language Models", "lora", [
        ("The Full Fine-Tuning Storage Crisis: Why Saving 100GB Checkpoints Per Task Was Dead", "architecture_breakdown", "Why duplicating all weights for every downstream task created an impossible storage and deployment bottleneck as models scaled to hundreds of billions of parameters."),
        ("The Intrinsic Rank Hypothesis: Decomposing Delta W into Thin Bottleneck Matrices B x A", "mechanism_deepdive", "The mathematical hypothesis that weight updates live on a low-dimensional manifold, proving that rank r=8 or r=16 captures full adaptation capacity."),
        ("Zero Inference Latency Overhead: The Mathematical Elegance of Merging W = W_0 + BA", "mechanism_deepdive", "How adapter weights can be linearly added directly into frozen base matrices for deployment, adding zero compute latency or memory overhead at inference."),
        ("Benchmark Parity: Matching Full Fine-Tuning on RoBERTa, DeBERTa, and GPT-3", "benchmark_news", "Empirical validation showing that LoRA matches or exceeds full fine-tuning performance across GLUE, SQuAD, and WikiSQL with 10,000x fewer trainable weights."),
        ("The Open-Source Fine-Tuning Boom: How LoRA Empowered Millions to Train LLMs on Consumer Hardware", "architecture_breakdown", "How LoRA and QLoRA democratized custom AI fine-tuning, allowing developers to adapt 70B models on modest single-GPU workstations.")
    ]),
    # 18. Chinchilla
    ("2203.15556", "Chinchilla: Compute-Optimal Large Language Models", "chinchilla", [
        ("The Gopher & GPT-3 Blunder: Why the World Was Training Undertrained Giant Models", "architecture_breakdown", "The eye-opening discovery that leading AI labs were scaling model parameters too aggressively while starving them of sufficient training tokens."),
        ("IsoFLOP Contour Hyperbolas: The 1:1 Mathematical Balance of Parameters and Tokens", "mechanism_deepdive", "Fitting parametric loss surfaces across over 400 training runs to prove that compute-optimal scaling requires parameters and tokens to scale in equal 1:1 proportion."),
        ("70B Outperforms 280B: The Dense Model Revolution That Defied Conventional Wisdom", "mechanism_deepdive", "The demonstration that a 70B parameter model trained on 1.4 trillion tokens systematically beats a 280B model trained on 300 billion tokens while cutting inference costs by 4x."),
        ("The Comprehensive Benchmark Sweep: Setting SOTA on MMLU, Big-Bench, and Reasoning", "benchmark_news", "Proving Chinchilla's superiority across diverse reasoning, reading comprehension, and commonsense benchmarks over Gopher, GPT-3, Megatron, and Jurassic-1."),
        ("The Blueprint for Llama and Mistral: How Chinchilla Shaped Modern Open-Weights AI", "architecture_breakdown", "How Meta and Mistral adopted Chinchilla scaling principles to train over-tokenized compact models (Llama 1, 2, 3), sparking the open-source LLM revolution.")
    ]),
    # 19. DPO
    ("2305.18290", "DPO: Direct Preference Optimization", "dpo", [
        ("The RLHF Fragility Trap: Why Training Actor, Critic, and Reward Models Concurrently Failed", "architecture_breakdown", "Why 3-model PPO pipelines suffered from severe training instability, hyperparameter sensitivity, and high GPU memory footprints."),
        ("The Closed-Form Analytic Derivation: Turning the Optimal Policy into an Implicit Reward", "mechanism_deepdive", "The mathematical breakthrough deriving the exact analytical relationship between optimal policy probabilities and the underlying Bradley-Terry ground-truth reward."),
        ("The Binary Cross-Entropy Alignment Loss: Replacing Policy Gradients with Stable Optimization", "mechanism_deepdive", "How DPO condenses the entire RLHF pipeline into a single, clean classification loss that pulls winning responses up and pushes losing responses down."),
        ("Benchmarking Preference Alignment: Beating PPO on TL;DR Summarization and Anthropic HH", "benchmark_news", "Demonstrating that DPO matches or exceeds PPO in human preference evaluations while training radically faster with zero reinforcement learning overhead."),
        ("The Post-RLHF Paradigm: How DPO Became the Universal Finetuning Standard for Modern LLMs", "architecture_breakdown", "How Zephyr, Starling, Llama 3, and DeepSeek adopted DPO and its variants (KTO, ORPO) as the primary alignment engine for open-weights models.")
    ]),
    # 20. NeRF
    ("2003.08934", "NeRF: Neural Radiance Fields for View Synthesis", "nerf", [
        ("The Death of Polygons: Why Classical 3D Meshes Failed on Fog, Glass, and Complex Lighting", "architecture_breakdown", "Why triangular polygon meshes struggle with fine geometric details, transparent refractions, and specular highlights in real-world scenes."),
        ("The 5D Continuous Function: Mapping (x, y, z, theta, phi) to (RGB, sigma) with an 8-Layer MLP", "mechanism_deepdive", "Representing continuous 3D scenes inside the weights of a simple neural network that predicts emitted color and volume density along camera sightlines."),
        ("Positional Frequency Encoding and Hierarchical Sampling: Capturing Micro-Textures Without Aliasing", "mechanism_deepdive", "Applying sinusoidal frequency projections to input coordinates to allow standard MLPs to learn high-frequency textures and geometric edges."),
        ("Photorealistic Novel View Synthesis: Generating Unseen 360-Degree Trajectories from Sparse Photos", "benchmark_news", "Evaluating NeRF across synthetic Blender objects and real forward-facing scenes, setting unprecedented PSNR and SSIM visual quality records."),
        ("The 3D Gaussian Splatting Genesis: How NeRF Sparked the Modern Spatial Computing Revolution", "architecture_breakdown", "How neural volumetric rendering evolved into instant 3D capture, Gaussian splatting, and neural spatial computing for virtual reality.")
    ])
]

def main():
    with open(TOPIC_QUEUE_FILE, "r", encoding="utf-8") as f:
        queue = json.load(f)

    existing_ids = {item["id"] for item in queue}
    new_items = []

    for arx_id, series_title, slug_prefix, episodes in GOAT_PAPERS:
        for idx, (ep_title, cat, angle) in enumerate(episodes):
            part_num = idx + 1
            item_id = f"goat_{slug_prefix}_part_{part_num}"
            if item_id in existing_ids:
                continue

            clean_topic = f"{series_title}: Part {part_num} - {ep_title}"
            series_name = f"GOAT Papers: {series_title} Mini-Series"
            part_str = f"{part_num}/5"

            entry = {
                "id": item_id,
                "arxiv_id": arx_id,
                "topic": clean_topic,
                "category": cat,
                "series": series_name,
                "part": part_str,
                "angle": angle,
                "status": "pending"
            }
            new_items.append(entry)
            existing_ids.add(item_id)

    print(f"Prepared {len(new_items)} new GOAT video topics across {len(GOAT_PAPERS)} papers.")
    queue.extend(new_items)

    with open(TOPIC_QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2)

    print(f"Successfully saved queue! Total active items in {TOPIC_QUEUE_FILE.name}: {len(queue)}")

if __name__ == "__main__":
    main()
