"""
Utility functions
"""
import os


def load_sample_pyqs():
    """Load sample PYQ data"""
    sample_data = {
        'DBMS': [
            {
                'year': 2023,
                'question': 'What are the ACID properties in a database?',
                'answer': 'ACID stands for Atomicity, Consistency, Isolation, and Durability. Atomicity ensures transactions are all-or-nothing. Consistency maintains data integrity. Isolation prevents interference between concurrent transactions. Durability ensures committed data survives failures.'
            },
            {
                'year': 2023,
                'question': 'Explain normalization and its forms.',
                'answer': 'Normalization is process of organizing data to reduce redundancy. 1NF: No repeating groups. 2NF: No partial dependencies. 3NF: No transitive dependencies. BCNF: Every determinant is a candidate key.'
            },
            {
                'year': 2022,
                'question': 'What is indexing in databases?',
                'answer': 'Indexing is technique to speed up query execution. Creates data structure (usually B-tree) that allows faster data retrieval. Primary index on primary key, secondary index on other attributes.'
            },
        ],
        'DS': [
            {
                'year': 2023,
                'question': 'Explain binary search and its complexity.',
                'answer': 'Binary search is efficient algorithm for sorted arrays. Divides search space in half each iteration. Time complexity: O(log n). Space complexity: O(1) for iterative, O(log n) for recursive.'
            },
            {
                'year': 2023,
                'question': 'What are different types of sorting algorithms?',
                'answer': 'Sorting algorithms include: Bubble Sort O(n²), Selection Sort O(n²), Insertion Sort O(n²), Merge Sort O(n log n), Quick Sort O(n log n average), Heap Sort O(n log n).'
            },
            {
                'year': 2022,
                'question': 'Explain balanced binary search trees.',
                'answer': 'Balanced BSTs maintain height balance to ensure O(log n) operations. Examples: AVL trees, Red-Black trees. AVL maintains |height difference| <= 1. Red-Black uses color constraints.'
            },
        ],
        'ML': [
            {
                'year': 2023,
                'question': 'What is overfitting and how to prevent it?',
                'answer': 'Overfitting occurs when model learns training data too well including noise. Prevention methods: regularization (L1/L2), dropout, early stopping, cross-validation, data augmentation, reducing model complexity.'
            },
            {
                'year': 2023,
                'question': 'Explain gradient descent and variants.',
                'answer': 'Gradient descent optimizes model by moving in negative gradient direction. Variants: SGD (single sample), Mini-batch GD, Adam (adaptive), RMSprop. Learning rate controls step size.'
            },
            {
                'year': 2022,
                'question': 'What is cross-validation?',
                'answer': 'Cross-validation evaluates model performance on different data subsets. K-fold: divide data into k parts, train on k-1, test on 1. Prevents overfitting, gives realistic performance estimate.'
            },
        ],
        'CN': [
            {
                'year': 2023,
                'question': 'Explain TCP three-way handshake.',
                'answer': 'TCP connection establishment: SYN from client, SYN-ACK from server, ACK from client. Ensures both parties ready for communication. Sequence numbers prevent duplicate packets.'
            },
            {
                'year': 2023,
                'question': 'What is sliding window protocol?',
                'answer': 'Flow control mechanism allowing multiple frames transmission without waiting for ACK. Sender window: frames sent not ACKed. Receiver window: frames can receive. Prevents buffer overflow.'
            },
            {
                'year': 2022,
                'question': 'Explain routing protocols.',
                'answer': 'Routing determines best path for packets. Distance Vector: RIP based on hop count. Link State: OSPF considers link cost. BGP for inter-autonomous systems. Dijkstra algorithm used.'
            },
        ],
        'OS': [
            {
                'year': 2023,
                'question': 'What is a deadlock and how to prevent it?',
                'answer': 'Deadlock: mutual waiting of processes for resources. Conditions: mutual exclusion, hold-and-wait, no preemption, circular wait. Prevention: break any condition. Detection: resource allocation graph.'
            },
            {
                'year': 2023,
                'question': 'Explain page replacement algorithms.',
                'answer': 'Algorithms for choosing page to remove when memory full: FIFO removes oldest, LRU removes least recently used, Optimal removes future least needed. LRU most practical, Belady anomaly in FIFO.'
            },
            {
                'year': 2022,
                'question': 'What is virtual memory?',
                'answer': 'Technique using disk as extension of RAM. Paging: divide memory into fixed-size pages. Swapping: move pages between RAM and disk. Enables running programs larger than physical memory.'
            },
        ]
    }
    
    texts = []
    metadata = []
    
    for subject, questions in sample_data.items():
        for item in questions:
            # Combine question and answer
            text = f"[{subject}] {item['question']}\n{item['answer']}"
            texts.append(text)
            metadata.append({
                'subject': subject,
                'year': item['year'],
                'text': text
            })
    
    return texts, metadata


def chunk_text(text, chunk_size=500, overlap=50):
    """Chunk text into smaller pieces"""
    chunks = []
    start = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        
        # Try to break at sentence boundary
        if end < len(text):
            last_period = text.rfind('.', start, end)
            if last_period > start + chunk_size // 2:
                end = last_period + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
    
    return chunks


def format_answer(answer):
    """Format answer for display"""
    # Remove excessive whitespace
    answer = ' '.join(answer.split())
    
    # Add line breaks for readability
    sentences = answer.split('. ')
    if len(sentences) > 3:
        answer = '.\n'.join(sentences)
    
    return answer
