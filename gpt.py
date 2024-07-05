import openai

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

openai.api_key  = "<Provide an API key its basically free.>"

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, # this is the degree of randomness of the model's output
    )
#     print(str(response.choices[0].message))
    return response.choices[0].message["content"]

notation = ["e2e4"]
import chess

def is_legal(move):
    board = chess.Board()
    board.push_san("e4")  # Make the move e4
    return chess.Move.from_uci("d7" + move) in board.legal_moves

def robot_turn():
    global notation
    robot_prompt = [
    {'role':'system', 'content': f'You are playing white in this chess game moves in uci as a list {notation}. what move will you play next.Give the uci with no supporting text or spaces.This should be plain text dont put it in quotation marks.Keep in mind uci has both the previous square and the next square for the piece moved.'}]

    robot_response = get_completion_from_messages(robot_prompt, temperature=1)

    notation.append(robot_response)

    print(notation)


