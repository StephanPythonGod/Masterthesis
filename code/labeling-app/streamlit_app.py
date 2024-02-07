import streamlit as st
import os
import json
import random
import pandas as pd

def file_selector(evaluator='A', folder_path='../data-reader', output_folder='./output-data'):
    indices_to_inspect = ["translated_IndexEnglishAllFiltered_long", "IndexEnglishAllFiltered_long"]
    leaf_folders = []
    evaluator_folder = os.path.join(output_folder, evaluator)
    for dirpath, dirnames, files in os.walk(folder_path):
        if not dirnames:
            relative_path = os.path.relpath(dirpath, folder_path)
            evaluator_path = os.path.join(evaluator_folder, relative_path)
            if not os.path.exists(evaluator_path):
                # if evaluator path includes one of the indices to inspect
                if any(index in evaluator_path for index in indices_to_inspect):
                    leaf_folders.append(dirpath)
    selected_folder = st.selectbox('Wählen Sie einen Ordner', leaf_folders)
    return selected_folder

def aggregate_jsons(folder_path):
    "Aggregate multiple jsons based on the keys"
    aggregated_data = {}
    print(f"Aggregating JSON files from {folder_path}...")
    for file_name in os.listdir(folder_path):   
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path) and file_name.endswith('.json'):
            try:
                # Try to load Json
                with open(file_path, "r") as json_file:
                    data = json.load(json_file)
                # Receive all keys of the json
                keys = data.keys()
                # Create lists for each key and add the current data value
                for key in keys:
                    if key not in aggregated_data:
                        aggregated_data[key] = []
                    aggregated_data[key].extend(data[key])
                print(f"Aggregated data from {file_name}")
            except json.JSONDecodeError:
                print(f"Could not decode JSON from file {file_path}")

    print("Finished aggregating JSON files.")
    
    if folder_path.split("/")[2] == "en":
        dropped_answer = "I can't provide an answer given the context."
    else:
        dropped_answer = "Ich kann keine Antwort geben, da der Kontext fehlt."
    
    print("Dropped answer: ", dropped_answer)
    
    print("Retrieving questions, answers, contexts, and gold_answers...")
    # Retrieve questions, answers, contexts and gold_answers
    questions = aggregated_data['questions']
    answers = aggregated_data['answers']
    contexts = aggregated_data['contexts']
    predictions = aggregated_data['generated_answers']

    print("Filtering data...")
    # Remove all answers that are equal to the dropped answer
    # Get all indices of dropped_context based on answers
    dropped_indices = set(i for i, x in enumerate(answers) if x == dropped_answer)

    # Create new lists without dropped_context and with only dropped_context
    filtered_questions, filtered_predictions, filtered_contexts, filtered_answers = [], [], [], []
    dropped_questions, dropped_predictions, dropped_contexts, dropped_answers = [], [], [], []

    for i in range(len(questions)):
        if i in dropped_indices:
            dropped_questions.append(questions[i])
            dropped_predictions.append(predictions[i])
            dropped_contexts.append(contexts[i])
            dropped_answers.append(answers[i])
        else:
            filtered_questions.append(questions[i])
            filtered_predictions.append(predictions[i])
            filtered_contexts.append(contexts[i])
            filtered_answers.append(answers[i])
        
    print("Sampling data...")
    # Sample randomly for every key 100 values. The index is important over all keys
    random.seed(42)

    # Get for all lists 50 samples
    sample_size_all = min(50, len(filtered_questions))
    indices = random.sample(range(len(filtered_questions)), sample_size_all)
    filtered_questions = [filtered_questions[index] for index in indices]
    filtered_predictions = [filtered_predictions[index] for index in indices]
    filtered_contexts = [filtered_contexts[index] for index in indices]
    filtered_answers = [filtered_answers[index] for index in indices]

    sample_size_dropped = min(50, len(dropped_questions))
    indices = random.sample(range(len(dropped_questions)), sample_size_dropped)
    dropped_questions = [dropped_questions[index] for index in indices]
    dropped_predictions = [dropped_predictions[index] for index in indices]
    dropped_contexts = [dropped_contexts[index] for index in indices]
    dropped_answers = [dropped_answers[index] for index in indices]

    print("Finalizing data...")
    questions = filtered_questions + dropped_questions
    predictions = filtered_predictions + dropped_predictions
    contexts = filtered_contexts + dropped_contexts
    answers = filtered_answers + dropped_answers

    print("Data processing completed.")
    return {"questions": questions, "predictions": predictions, "gold_answer": answers, "contexts": contexts}, sample_size_all

    # Get 100 random indices from the length of the first key
    # sample_size = min(50, len(filtered_questions)))
    # indices = random.sample(range(population_size), sample_size)
    # # Create a new dictionary with the sampled values
    # aggregated_data_sampled = {}
    # for key in aggregated_data:
    #     aggregated_data_sampled[key] = [aggregated_data[key][index] for index in indices]
    # return aggregated_data_sampled

def get_evaluator_leaf_paths(evaluator='A', folder_path='../data-reader', output_folder='./output-data'):
    leaf_paths = []
    evaluator_folder = os.path.join(output_folder, evaluator)
    for dirpath, dirnames, files in os.walk(evaluator_folder):
        if not dirnames:
            leaf_paths.append(dirpath)
    return leaf_paths

if __name__ == "__main__":
    st.title('Dateiauswahl-App')
    # Add a selector for "A" or "B"
    evaluator = st.selectbox('Evaluator', ('A', 'B'))
    st.write('Sie haben `%s` als Evaluator ausgewählt' % evaluator)
    evaluator_leaf_paths = get_evaluator_leaf_paths(evaluator)
    st.write('Die existierenden Blatt-Pfade des ausgewählten Evaluators sind:')
    if not evaluator_leaf_paths:
        st.write('Keine Blatt-Pfade gefunden')
    for path in evaluator_leaf_paths:
        st.write(path)
    selected_folder = file_selector()
    st.write('Sie haben `%s` ausgewählt' % selected_folder)
    # aggregated_data = aggregate_jsons(selected_folder)
    aggregated_data, sample_size = aggregate_jsons(selected_folder)
    # Display the aggregated data - for every key only the first 10 values


    df = pd.DataFrame(aggregated_data)

    # Create a new column for checkboxes
    df['Correct?'] = [False for _ in range(len(df))]
    df['Gold Answer Correct?'] = [False for _ in range(len(df))]
    df['Question Useful?'] = [False for _ in range(len(df))]

    # Convert the lists in the 'contexts' column to strings with line breaks between them
    print(f"Columns: {df.columns}")
    df['contexts'] = df['contexts'].apply(lambda x: '\n\n'.join(x))

    # Display the DataFrame in an editable format
    df = st.data_editor(df)



        # Add a "Submit" button
    if st.button('Submit'):
        # Count the number of checked checkboxes for all rows below sample_size
        num_checked_all = df['Correct?'][:sample_size].sum()

        num_checked_dropped = df['Correct?'][sample_size:].sum()

        # Average the number of checked checkboxes
        avg_checked_all = num_checked_all / sample_size
        avg_checked_dropped = num_checked_dropped / ( len(df) - sample_size)

        # num_checked true only where gold answer is true for only sample size
        num_checked_gold_answer_all = len(df[(df["Correct?"] == True) & (df["Gold Answer Correct?"] == True) & (df["Question Useful?"] == True)].loc[:sample_size])

        num_checked_gold_answer_dropped = len(df[(df["Correct?"] == True) & (df["Correct?"] == True) & (df['Gold Answer Correct?'] == True) & (df["Question Useful?"] == True)].loc[sample_size+1:])

        print(f"Checked gold answer all: {num_checked_gold_answer_all}")

        print(f"Avg checked gold answer all: {df['Gold Answer Correct?'][:sample_size].sum()}")
        # Average the number of checked checkboxes over only the number of true gold answers
        try:
            avg_checked_gold_answer_all = num_checked_gold_answer_all / len(df[(df["Gold Answer Correct?"] == True) & (df["Question Useful?"] == True)].loc[:sample_size])
        except:
            avg_checked_gold_answer_all = 0.0

        try:
            avg_checked_gold_answer_dropped = num_checked_gold_answer_dropped / len(df[(df["Gold Answer Correct?"] == True) & (df["Question Useful?"] == True)].loc[sample_size+1:])
        except:
            avg_checked_gold_answer_dropped = 0.0 
        
        try:
            avg_checked_question_true_all = num_checked_all / len(df[df["Question Useful?"] == True].loc[:sample_size])
        except:
            avg_checked_question_true_all = 0.0
        
        try:
            avg_checked_question_true_dropped = num_checked_dropped / len(df[df["Question Useful?"] == True].loc[sample_size+1:])
        except:
            avg_checked_question_true_dropped = 0.0

        st.write('Anzahl der angeklickten Checkboxen: %s' % str(num_checked_all + num_checked_dropped))
        st.write('Durchschnittliche Anzahl der angeklickten Checkboxen: %s' % str(avg_checked_all + avg_checked_dropped))

        output = {
            "all": 
            {
                "all": {
                    'amount': sample_size,
                    'human_accuracy': avg_checked_all
                },
                "question_true":{
                    "amount": len(df[df["Question Useful?"] == True].loc[:sample_size]),
                    "human_accuracy": avg_checked_question_true_all
                },
                "gold_answer_and_question_true": {
                    "amount": len(df[(df["Gold Answer Correct?"] == True) & (df["Question Useful?"] == True)].loc[:sample_size]),
                    'human_accuracy': avg_checked_gold_answer_all
                }
            },
            "dropped_contexts":{
                "all": {
                    'amount': len(df) - sample_size,
                    'human_accuracy': avg_checked_dropped
                },
                "question_true":{
                    "amount": len(df[df["Question Useful?"] == True].loc[sample_size+1:]),
                    "human_accuracy": avg_checked_question_true_dropped
                },
                "gold_answer_and_question_true": {
                    "amount": len(df[(df["Gold Answer Correct?"] == True) & (df["Question Useful?"] == True)].loc[sample_size+1:]),
                    'human_accuracy': avg_checked_gold_answer_dropped
                }
            },
            "stats":{
                "amount": len(df),
                "gold_answers_true": int(df["Gold Answer Correct?"].sum()),
                "question_true": int(df["Question Useful?"].sum()) 
            }
        }       
        # Join the remaining components back into a path
        selected_folder_subpath = selected_folder.replace('../data-reader/', '')

        # Create the output folder path
        output_folder_path = os.path.join('./output-data', evaluator, selected_folder_subpath)

        print(f"Output folder path: {output_folder_path}")

        # Ensure the output folder exists
        os.makedirs(output_folder_path, exist_ok=True)

        # Create the output file path
        output_file_path = os.path.join(output_folder_path, 'output.json')

        st.write("Ausgabe: ", output)

        # Write the output dictionary to the output file
        with open(output_file_path, 'w') as f:
            json.dump(output, f, indent=4)

        st.write('Die Ausgabe wurde in die Datei %s geschrieben.' % output_file_path)