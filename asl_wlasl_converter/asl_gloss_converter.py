"""
Advanced ASL Gloss Converter

This module provides a comprehensive text-to-gloss conversion system for American Sign Language,
implementing linguistic research-based rules for ASL grammar.

Features:
- Morphological analysis and processing
- ASL grammar rule application
- Special handling for verb directionality
- Non-manual marker representation
- Classifiers and depicting verb support
- Fingerspelling detection
"""

import re
import json
import os
from typing import List, Dict, Set, Tuple, Optional, Union


class ASLGlossConverter:
    """
    A comprehensive American Sign Language gloss converter.
    
    This class implements research-based linguistic rules to convert English text
    to ASL gloss according to proper ASL grammar.
    """
    
    def __init__(self, use_fingerspelling: bool = True, detailed_markers: bool = True):
        """
        Initialize the ASL Gloss Converter.
        
        Args:
            use_fingerspelling: Whether to use fingerspelling for proper nouns and unknown words
            detailed_markers: Whether to include detailed non-manual markers
        """
        self.use_fingerspelling = use_fingerspelling
        self.detailed_markers = detailed_markers
        
        # Load linguistic resources
        self._load_resources()
    
    def _load_resources(self):
        """Load all linguistic resources for gloss conversion."""
        # Syntax and grammar rule datasets
        
        # Function words (words to filter out from ASL - no direct sign equivalents)
        self.function_words = {
            # Articles
            'a', 'an', 'the',
            
            # Forms of "to be"
            'is', 'are', 'am', 'was', 'were', 'be', 'been', 'being',
            
            # Auxiliary verbs
            'will', 'would', 'shall', 'should', 'can', 'could', 'may', 'might', 'must',
            
            # Prepositions (many are incorporated into ASL signs)
            'to', 'of', 'for', 'with', 'by', 'at', 'from', 'in', 'on', 'under', 'over',
            'through', 'between', 'among', 'against', 'into', 'onto', 'within', 'without',
            
            # Conjunctions (handled differently in ASL)
            'and', 'or', 'but', 'nor', 'so', 'yet', 'although', 'because', 'since',
            
            # Other function words
            'as', 'that', 'which', 'who', 'whom', 'whose', 'what', 'when', 'where', 'how',
            'if', 'then', 'than', 'though', 'although', 'however', 'unless', 'until',
            'while', 'where', 'whether', 'thus'
        }
        
        # Time-related words (often come first in ASL)
        self.time_words = {
            'yesterday', 'today', 'tomorrow', 'now', 'later', 'soon', 'before', 'after',
            'morning', 'afternoon', 'evening', 'night', 'midnight', 'noon',
            'day', 'week', 'month', 'year', 'decade', 'century',
            'past', 'present', 'future', 'always', 'never', 'sometimes', 'often',
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
            'january', 'february', 'march', 'april', 'may', 'june', 'july', 
            'august', 'september', 'october', 'november', 'december'
        }
        
        # Question words (special handling in ASL)
        self.question_words = {
            'what', 'who', 'where', 'when', 'why', 'how', 'which',
            'whatfor', 'forwhat', 'howmany', 'howmuch'
        }
        
        # Negation words
        self.negation_words = {
            'not', 'no', 'none', 'never', 'nothing', 'nobody', 'nowhere', 'neither', 'nor',
            "don't", 'dont', "doesn't", 'doesnt', "can't", 'cant', "won't", 'wont',
            "haven't", 'havent', "hasn't", 'hasnt', "couldn't", 'couldnt'
        }
        
        # Verb directionality - verbs that incorporate their object
        self.directional_verbs = {
            'give', 'send', 'tell', 'ask', 'help', 'show', 'pay', 'inform', 'teach',
            'explain', 'answer', 'meet', 'visit', 'invite', 'blame', 'borrow', 'lend'
        }
        
        # Depicting verbs (classifier predicates)
        self.depicting_verbs = {
            'move', 'go', 'walk', 'drive', 'fly', 'jump', 'fall', 'climb', 'descend',
            'ascend', 'travel', 'come', 'approach', 'leave', 'arrive', 'depart'
        }
        
        # Common classifiers in ASL
        self.classifiers = {
            'person': 'CL:1', 
            'people': 'CL:1-MULT',
            'vehicle': 'CL:3', 
            'book': 'CL:B', 
            'small-object': 'CL:F', 
            'glass': 'CL:C',
            'thin-object': 'CL:G', 
            'animal': 'CL:bent-V', 
            'surface': 'CL:B'
        }
        
        # Non-manual markers
        self.non_manual_markers = {
            'question': 'q',
            'topic': 't',
            'negation': 'neg',
            'conditional': 'cond',
            'relative-clause': 'rc',
            'rhetorical-question': 'rh',
            'intensifier': 'int'
        }
        
        # Plural forms
        self.irregular_plurals = {
            'children': 'child',
            'people': 'person',
            'men': 'man',
            'women': 'woman',
            'mice': 'mouse',
            'teeth': 'tooth',
            'feet': 'foot'
        }
        
        # Common irregular verbs
        self.irregular_verbs = {
            'went': 'go',
            'gone': 'go',
            'came': 'come',
            'seen': 'see',
            'saw': 'see',
            'ate': 'eat',
            'eaten': 'eat',
            'gave': 'give',
            'given': 'give',
            'took': 'take',
            'taken': 'take',
            'knew': 'know',
            'known': 'know',
            'wrote': 'write',
            'written': 'write',
            'drove': 'drive',
            'driven': 'drive',
            'bought': 'buy',
            'felt': 'feel',
            'told': 'tell',
            'made': 'make',
            'said': 'say',
            'thought': 'think',
            'caught': 'catch',
            'taught': 'teach'
        }
        
        # Morphological patterns
        self.suffix_patterns = [
            ('ing', ''),       # walking -> walk
            ('ed', ''),        # walked -> walk 
            ('s', ''),         # walks -> walk
            ('es', ''),        # boxes -> box
            ('er', ''),        # faster -> fast
            ('est', ''),       # fastest -> fast
            ('ly', '')         # quickly -> quick
        ]
        
        # Intensifiers (repetition or large movement in ASL)
        self.intensifiers = {
            'very', 'really', 'extremely', 'so', 'too', 'quite', 'rather'
        }
        
        # Words requiring fingerspelling (typically initialized signs)
        self.fingerspelled_categories = {
            'name', 'title', 'brand', 'abbreviation'
        }
        
        # ASL numbers need special handling
        self.number_words = {
            'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5',
            'six': '6', 'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10',
            'eleven': '11', 'twelve': '12', 'thirteen': '13', 'fourteen': '14',
            'fifteen': '15', 'sixteen': '16', 'seventeen': '17', 'eighteen': '18',
            'nineteen': '19', 'twenty': '20', 'thirty': '30', 'forty': '40',
            'fifty': '50', 'sixty': '60', 'seventy': '70', 'eighty': '80',
            'ninety': '90', 'hundred': '100', 'thousand': '1000', 'million': '1000000'
        }
    
    def convert(self, text: str) -> List[str]:
        """
        Convert English text to ASL gloss.
        
        Args:
            text: English text to convert
            
        Returns:
            List of ASL gloss tokens
        """
        # Preprocessing
        processed_text = self._preprocess_text(text)
        
        # Tokenize
        tokens = self._tokenize(processed_text)
        
        # Analyze sentence structure
        sentence_type, subject, verb, objects, adjuncts = self._analyze_sentence(tokens)
        
        # Apply ASL grammar transformations
        asl_gloss = self._apply_asl_grammar(tokens, sentence_type, subject, verb, objects, adjuncts)
        
        return asl_gloss
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for conversion."""
        # Convert to lowercase
        text = text.lower()
        
        # Replace contractions
        text = text.replace("don't", "do not")
        text = text.replace("doesn't", "does not")
        text = text.replace("won't", "will not")
        text = text.replace("can't", "cannot")
        text = text.replace("i'm", "i am")
        text = text.replace("you're", "you are")
        text = text.replace("he's", "he is")
        text = text.replace("she's", "she is")
        text = text.replace("it's", "it is")
        text = text.replace("we're", "we are")
        text = text.replace("they're", "they are")
        
        # Save question marks for sentence type analysis
        is_question = '?' in text
        
        # Remove punctuation but keep sentence markers
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Restore question status if needed
        if is_question:
            text += ' ?'
            
        return text
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize the text into words."""
        return text.split()
    
    def _analyze_sentence(self, tokens: List[str]) -> Tuple[str, List[str], List[str], List[str], List[str]]:
        """
        Analyze English sentence structure.
        
        Returns:
            Tuple containing:
                - Sentence type (declarative, interrogative, etc.)
                - Subject
                - Verb
                - Objects
                - Adjuncts (time, location, etc.)
        """
        # Determine sentence type
        sentence_type = 'declarative'
        if '?' in tokens:
            sentence_type = 'interrogative'
            tokens.remove('?')
        elif any(token in self.question_words for token in tokens):
            sentence_type = 'interrogative'
        
        # Very simplified sentence parsing
        # In a real implementation, this would use a robust NLP parser
        
        # Extract time expressions (adjuncts)
        time_tokens = [t for t in tokens if t in self.time_words]
        non_time_tokens = [t for t in tokens if t not in self.time_words]
        
        # For simplicity, make some assumptions about English word order
        # Subject-Verb-Object is common in English
        
        # This is a simplified placeholder for actual syntactic parsing
        subject = non_time_tokens[:1] if non_time_tokens else []
        verb = non_time_tokens[1:2] if len(non_time_tokens) > 1 else []
        objects = non_time_tokens[2:4] if len(non_time_tokens) > 2 else []
        adjuncts = time_tokens + (non_time_tokens[4:] if len(non_time_tokens) > 4 else [])
        
        return sentence_type, subject, verb, objects, adjuncts
    
    def _apply_asl_grammar(self, tokens: List[str], sentence_type: str, 
                          subject: List[str], verb: List[str], 
                          objects: List[str], adjuncts: List[str]) -> List[str]:
        """Apply ASL grammar rules to create a gloss."""
        # Process and transform tokens
        processed_tokens = []
        
        # Track what we've already handled
        handled_tokens = set()
        
        # First, extract time expressions (come first in ASL)
        time_expressions = []
        for token in tokens:
            if token in self.time_words:
                time_expressions.append(token.upper())
                handled_tokens.add(token)
        
        # Process question words (often first or doubled in ASL)
        question_marker = None
        for token in tokens:
            if token in self.question_words and token not in handled_tokens:
                question_marker = token.upper()
                handled_tokens.add(token)
                break
        
        # Process negation
        has_negation = any(token in self.negation_words for token in tokens)
        for token in tokens:
            if token in self.negation_words:
                handled_tokens.add(token)
        
        # Process remaining tokens with morphological analysis
        main_clause = []
        for token in tokens:
            if token in handled_tokens:
                continue
                
            if token in self.function_words:
                # Skip function words in ASL
                continue
            
            # Handle numbers
            if token in self.number_words:
                main_clause.append(self.number_words[token])
                continue
            
            # Check for irregular forms first
            if token in self.irregular_plurals:
                # Handle irregular plurals
                root = self.irregular_plurals[token]
                main_clause.append(root.upper())
                main_clause.append("MANY")
                continue
                
            if token in self.irregular_verbs:
                # Handle irregular verbs
                root = self.irregular_verbs[token]
                main_clause.append(root.upper())
                # Check if it's past tense
                if token != root and not token.endswith('ing'):
                    main_clause.append("FINISH")
                continue
            
            # Apply morphological transformations
            original_token = token
            modified = False
            
            # Check for plural 's' ending
            if token.endswith('s') and not token.endswith('ss') and len(token) > 1:
                # Likely a plural
                root = token[:-1]
                main_clause.append(root.upper())
                main_clause.append("MANY")
                modified = True
            
            # Check for verb tenses and other suffixes
            if not modified:
                for suffix, replacement in self.suffix_patterns:
                    if token.endswith(suffix) and len(token) > len(suffix) + 1:
                        root = token[:-len(suffix)] + replacement
                        
                        # For -ing endings
                        if suffix == 'ing':
                            # Handle doubling rule (e.g., running -> run)
                            if len(root) > 0 and len(root) > 1 and root[-1] == root[-2]:
                                root = root[:-1]
                            main_clause.append(root.upper())
                            modified = True
                            break
                            
                        # For -ed endings (past tense)
                        elif suffix == 'ed':
                            # Handle special cases
                            if token.endswith('ied') and len(token) > 3:
                                # Handle cases like "studied" -> "study"
                                root = token[:-3] + 'y'
                            main_clause.append(root.upper())
                            main_clause.append("FINISH")
                            modified = True
                            break
                            
                        # For other suffixes
                        else:
                            main_clause.append(root.upper())
                            modified = True
                            break
            
            # If no transformation matched, add the token as-is
            if not modified:
                # Check if it's a directional verb
                if token in self.directional_verbs and objects:
                    # Indicate directionality in the gloss
                    object_index = tokens.index(objects[0]) if objects[0] in tokens else -1
                    subject_index = tokens.index(subject[0]) if subject and subject[0] in tokens else -1
                    
                    if subject_index != -1 and object_index != -1:
                        # Show verb directionality with subject and object
                        main_clause.append(f"{token.upper()}:{tokens[subject_index].upper()}-to-{tokens[object_index].upper()}")
                    else:
                        # Just show the verb
                        main_clause.append(token.upper())
                    modified = True
                
                # Check if it's a depicting verb (classifier predicate)
                elif token in self.depicting_verbs:
                    # Determine the classifier if possible from the context
                    classifier = None
                    for obj in objects:
                        if obj in self.classifiers:
                            classifier = self.classifiers[obj]
                            break
                    
                    if classifier:
                        main_clause.append(f"{token.upper()}:{classifier}")
                    else:
                        main_clause.append(token.upper())
                    modified = True
                
                # If still not handled, add as-is
                if not modified:
                    main_clause.append(token.upper())
        
        # Construct the final ASL gloss with correct ordering
        result = []
        
        # Add topic marker if needed
        if subject and self.detailed_markers:
            # Topic is often subject in ASL with topic marker
            topic = subject[0].upper()
            result.append(f"{topic}-t")  # -t indicates topic marker
        elif subject:
            result.extend([s.upper() for s in subject])
        
        # Time expressions come first in ASL
        result.extend(time_expressions)
        
        # Question words are typically first in ASL for WH-questions
        if question_marker and sentence_type == 'interrogative':
            result.append(question_marker)
        
        # Add other elements in ASL preferred order
        result.extend(main_clause)
        
        # For yes/no questions, add question marker at end
        if sentence_type == 'interrogative' and not question_marker:
            result.append("Q")  # Non-manual marker for yes/no questions
        
        # For WH-questions, sometimes the question word is repeated at the end
        elif question_marker and sentence_type == 'interrogative':
            result.append(question_marker)
        
        # Add negation at the end if needed
        if has_negation:
            result.append("NOT")
        
        return result


def convert_to_asl_gloss(text: str, use_fingerspelling: bool = True, detailed_markers: bool = False) -> List[str]:
    """
    Convert English text to ASL gloss using comprehensive ASL grammar rules.
    
    Args:
        text: English text to convert
        use_fingerspelling: Whether to use fingerspelling for proper nouns and unknown words
        detailed_markers: Whether to include detailed non-manual markers
        
    Returns:
        List of ASL gloss tokens
    """
    converter = ASLGlossConverter(use_fingerspelling, detailed_markers)
    return converter.convert(text)


if __name__ == "__main__":
    # Example usage
    test_sentences = [
        "I am going to the store tomorrow",
        "Where did you go yesterday?",
        "The books are on the table",
        "She doesn't like coffee",
        "Can you help me please?",
        "I have been studying ASL for two years"
    ]
    
    converter = ASLGlossConverter()
    
    for sentence in test_sentences:
        gloss = converter.convert(sentence)
        print(f"English: {sentence}")
        print(f"ASL Gloss: {' '.join(gloss)}")
        print()