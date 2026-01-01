from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
import pandas as pd

app = Flask(__name__)

# Load model and preprocessing objects
try:
    model = joblib.load('model.pkl')
    scaler = joblib.load('scaler.pkl')
    encoder = joblib.load('encoder.pkl')
    feature_names = joblib.load('feature_names.pkl')
    class_names = joblib.load('class_names.pkl')
    gpa_ranges = joblib.load('gpa_ranges.pkl')
    print("Models loaded successfully!")
    print(f"Available classes: {class_names}")
except FileNotFoundError as e:
    print(f"Error loading model files: {e}")
    print("Please run model_training.py first!")
    exit()

# Define valid ranges based on your dataset statistics
VALID_RANGES = {
    'attendance_percentage': {'min': 0, 'max': 100, 'step': 1},
    'sleep_time_hours': {'min': 0, 'max': 24, 'step': 0.1},
    'study_hours_per_week': {'min': 0, 'max': 50, 'step': 1},
    'total_credits': {'min': 0, 'max': 40, 'step': 1},
    'high_credit_modules': {'min': 0, 'max': 10, 'step': 1},
    'low_credit_modules': {'min': 0, 'max': 10, 'step': 1},
    'repeat_module_credits': {'min': 0, 'max': 20, 'step': 1},
    'lab_credits': {'min': 0, 'max': 20, 'step': 1},
    'part_time_job': {'min': 0, 'max': 1, 'step': 1},
    'internet_access': {'min': 0, 'max': 1, 'step': 1}
}


@app.route('/')
def home():
    # Prepare GPA info for template
    gpa_info = {}
    for category in class_names:
        if category in gpa_ranges:
            gpa_info[category] = gpa_ranges[category]

    return render_template('index.html',
                           classes=class_names,
                           ranges=VALID_RANGES,
                           gpa_info=gpa_info)


@app.route('/ranges', methods=['GET'])
def get_ranges():
    return jsonify(VALID_RANGES)


@app.route('/gpa_info', methods=['GET'])
def get_gpa_info():
    # Return GPA information for all classes
    gpa_info = {}
    for category in class_names:
        if category in gpa_ranges:
            gpa_info[category] = gpa_ranges[category]
    return jsonify(gpa_info)


@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get data from form
        data = {}
        validation_errors = []

        for feature in feature_names:
            value = request.form.get(feature)

            # Check if value is provided
            if value is None or value == '':
                validation_errors.append(f'Missing value for {feature}')
                continue

            # Validate and convert
            try:
                # Convert to appropriate type
                if feature in ['part_time_job', 'internet_access']:
                    data[feature] = int(float(value))
                    # Validate binary values
                    if data[feature] not in [0, 1]:
                        validation_errors.append(
                            f'{feature} must be 0 or 1, got {value}')
                else:
                    data[feature] = float(value)

                # Check range
                if feature in VALID_RANGES:
                    min_val = VALID_RANGES[feature]['min']
                    max_val = VALID_RANGES[feature]['max']

                    if data[feature] < min_val or data[feature] > max_val:
                        validation_errors.append(
                            f'{feature} must be between {min_val} and {max_val}, got {value}'
                        )

            except ValueError:
                validation_errors.append(
                    f'Invalid value for {feature}: {value}')

        # Return validation errors if any
        if validation_errors:
            return jsonify({'error': 'Validation failed', 'details': validation_errors}), 400

        # Create DataFrame with correct column order
        input_df = pd.DataFrame([data])[feature_names]

        # Scale features
        scaled_features = scaler.transform(input_df)

        # Make prediction
        prediction_encoded = model.predict(scaled_features)[0]
        prediction = encoder.inverse_transform([prediction_encoded])[0]

        # Get prediction probabilities
        probabilities = model.predict_proba(scaled_features)[0]
        prob_dict = {class_names[i]: f"{prob:.1%}"
                     for i, prob in enumerate(probabilities)}

        return jsonify({
            'prediction': prediction,
            'probabilities': prob_dict,
            'features_used': data,
            'valid_ranges': VALID_RANGES
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/sample', methods=['GET'])
def get_sample():
    # Provide realistic sample values based on dataset
    sample = {
        'attendance_percentage': 78,
        'sleep_time_hours': 6.5,
        'study_hours_per_week': 25,
        'total_credits': 30,
        'high_credit_modules': 3,
        'low_credit_modules': 2,
        'repeat_module_credits': 0,
        'lab_credits': 6,
        'part_time_job': 0,
        'internet_access': 1
    }
    return jsonify(sample)


@app.route('/classes', methods=['GET'])
def get_classes():
    return jsonify({'classes': class_names})


@app.route('/dataset_stats', methods=['GET'])
def get_dataset_stats():
    # Calculate actual statistics from dataset for better guidance
    df = pd.read_csv('student_performance_dataset_final.csv')

    stats = {}
    for feature in feature_names:
        if feature in df.columns:
            stats[feature] = {
                'min': float(df[feature].min()),
                'max': float(df[feature].max()),
                'mean': float(df[feature].mean()),
                'median': float(df[feature].median()),
                'std': float(df[feature].std())
            }

    return jsonify(stats)


if __name__ == '__main__':
    print("\nStarting Flask server...")
    print(f"Predicting classes: {class_names}")
    print("\nGPA Ranges:")
    for category in class_names:
        if category in gpa_ranges:
            info = gpa_ranges[category]
            print(f"  {category}: GPA {info['range']} - {info['description']}")
    print("\nFeature ranges:")
    for feature, ranges in VALID_RANGES.items():
        print(f"  {feature}: {ranges['min']} to {ranges['max']}")
    app.run(debug=True, port=5000)
