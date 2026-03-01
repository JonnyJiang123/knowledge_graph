export interface Token {
  text: string;
  start: number;
  end: number;
  pos?: string;
}

export interface Tokenizer {
  tokenize(text: string): Promise<Token[]>;
  segment(text: string): Promise<string[]>;
}
