import React, { useState } from 'react';
import { CheckCircle, XCircle, Clock, RotateCcw, Trophy, Star } from 'lucide-react';

const QuizInterface = ({ session, onViewChange }) => {
  const [currentQuiz, setCurrentQuiz] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [timeLeft, setTimeLeft] = useState(0);
  const [score, setScore] = useState(0);

  const startQuiz = async (topic, difficulty, subject) => {
    try {
      const response = await fetch('/api/quiz/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic,
          difficulty,
          subject,
          session_id: session.session_id,
          num_questions: 5
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate quiz');
      }

      const quiz = await response.json();
      setCurrentQuiz(quiz);
      setCurrentQuestion(0);
      setSelectedAnswers({});
      setShowResults(false);
      setTimeLeft(quiz.time_limit || 300);
      setScore(0);
    } catch (error) {
      console.error('Error starting quiz:', error);
    }
  };

  const selectAnswer = (questionId, answerIndex) => {
    setSelectedAnswers(prev => ({
      ...prev,
      [questionId]: answerIndex
    }));
  };

  const nextQuestion = () => {
    if (currentQuiz && currentQuestion < currentQuiz.questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const previousQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const submitQuiz = () => {
    setShowResults(true);
    // Calculate score logic would go here
  };

  if (showResults) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="text-center mb-8">
          <Trophy className="h-16 w-16 text-yellow-500 mx-auto mb-4" />
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Quiz Complete!</h2>
          <p className="text-gray-600">Here are your results</p>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="text-center">
              <div className="text-4xl font-bold text-blue-600 mb-2">{score}%</div>
              <div className="text-gray-600">Overall Score</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-green-600 mb-2">
                {Object.keys(selectedAnswers).length}
              </div>
              <div className="text-gray-600">Questions Answered</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-purple-600 mb-2">
                {currentQuiz?.questions.length || 0}
              </div>
              <div className="text-gray-600">Total Questions</div>
            </div>
          </div>

          <div className="space-y-4">
            {currentQuiz?.questions.map((question, index) => {
              const userAnswer = selectedAnswers[question.question_id];
              const isCorrect = userAnswer === question.correct_answer;
              
              return (
                <div key={question.question_id} className="border rounded-lg p-4">
                  <div className="flex items-start space-x-3">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                      isCorrect ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'
                    }`}>
                      {isCorrect ? (
                        <CheckCircle className="h-4 w-4" />
                      ) : (
                        <XCircle className="h-4 w-4" />
                      )}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900 mb-2">
                        Question {index + 1}: {question.question}
                      </h3>
                      <div className="space-y-2">
                        {question.options.map((option, optionIndex) => (
                          <div
                            key={optionIndex}
                            className={`p-2 rounded ${
                              optionIndex === question.correct_answer
                                ? 'bg-green-50 text-green-800 border border-green-200'
                                : optionIndex === userAnswer
                                ? 'bg-red-50 text-red-800 border border-red-200'
                                : 'bg-gray-50 text-gray-700'
                            }`}
                          >
                            {option}
                          </div>
                        ))}
                      </div>
                      {question.explanation && (
                        <div className="mt-3 p-3 bg-blue-50 rounded text-sm text-blue-800">
                          <strong>Explanation:</strong> {question.explanation}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="mt-8 flex justify-center space-x-4">
            <button
              onClick={() => {
                setShowResults(false);
                setCurrentQuiz(null);
                setCurrentQuestion(0);
                setSelectedAnswers({});
              }}
              className="btn-primary"
            >
              <RotateCcw className="h-4 w-4 mr-2" />
              Take Another Quiz
            </button>
            <button
              onClick={() => onViewChange('chat')}
              className="btn-secondary"
            >
              Back to Chat
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (currentQuiz) {
    const question = currentQuiz.questions[currentQuestion];
    const userAnswer = selectedAnswers[question.question_id];

    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-white rounded-lg shadow-lg p-8">
          {/* Quiz Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Quiz: {currentQuiz.topic}</h2>
              <p className="text-gray-600">Question {currentQuestion + 1} of {currentQuiz.questions.length}</p>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Clock className="h-4 w-4" />
              <span>{Math.floor(timeLeft / 60)}:{(timeLeft % 60).toString().padStart(2, '0')}</span>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mb-8">
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ width: `${((currentQuestion + 1) / currentQuiz.questions.length) * 100}%` }}
              />
            </div>
          </div>

          {/* Question */}
          <div className="mb-8">
            <h3 className="text-xl font-semibold text-gray-900 mb-6">
              {question.question}
            </h3>
            
            <div className="space-y-3">
              {question.options.map((option, index) => (
                <button
                  key={index}
                  onClick={() => selectAnswer(question.question_id, index)}
                  className={`quiz-option ${
                    userAnswer === index ? 'quiz-option-selected' : ''
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <div className={`w-4 h-4 rounded-full border-2 ${
                      userAnswer === index 
                        ? 'border-blue-500 bg-blue-500' 
                        : 'border-gray-300'
                    }`}>
                      {userAnswer === index && (
                        <div className="w-full h-full rounded-full bg-white scale-50" />
                      )}
                    </div>
                    <span>{option}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Navigation */}
          <div className="flex justify-between">
            <button
              onClick={previousQuestion}
              disabled={currentQuestion === 0}
              className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            
            <div className="flex space-x-2">
              {currentQuestion === currentQuiz.questions.length - 1 ? (
                <button
                  onClick={submitQuiz}
                  className="btn-primary"
                >
                  Submit Quiz
                </button>
              ) : (
                <button
                  onClick={nextQuestion}
                  className="btn-primary"
                >
                  Next Question
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="text-center mb-8">
        <Star className="h-16 w-16 text-yellow-500 mx-auto mb-4" />
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Quiz Generator</h1>
        <p className="text-gray-600">Test your knowledge with AI-generated quizzes</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Quick Quiz Options */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Math</h3>
          <div className="space-y-2">
            <button
              onClick={() => startQuiz('Algebra', 'easy', 'math')}
              className="w-full btn-secondary text-left"
            >
              Algebra - Easy
            </button>
            <button
              onClick={() => startQuiz('Geometry', 'medium', 'math')}
              className="w-full btn-secondary text-left"
            >
              Geometry - Medium
            </button>
            <button
              onClick={() => startQuiz('Calculus', 'hard', 'math')}
              className="w-full btn-secondary text-left"
            >
              Calculus - Hard
            </button>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Science</h3>
          <div className="space-y-2">
            <button
              onClick={() => startQuiz('Biology', 'easy', 'science')}
              className="w-full btn-secondary text-left"
            >
              Biology - Easy
            </button>
            <button
              onClick={() => startQuiz('Chemistry', 'medium', 'science')}
              className="w-full btn-secondary text-left"
            >
              Chemistry - Medium
            </button>
            <button
              onClick={() => startQuiz('Physics', 'hard', 'science')}
              className="w-full btn-secondary text-left"
            >
              Physics - Hard
            </button>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Programming</h3>
          <div className="space-y-2">
            <button
              onClick={() => startQuiz('Python', 'easy', 'programming')}
              className="w-full btn-secondary text-left"
            >
              Python - Easy
            </button>
            <button
              onClick={() => startQuiz('JavaScript', 'medium', 'programming')}
              className="w-full btn-secondary text-left"
            >
              JavaScript - Medium
            </button>
            <button
              onClick={() => startQuiz('Algorithms', 'hard', 'programming')}
              className="w-full btn-secondary text-left"
            >
              Algorithms - Hard
            </button>
          </div>
        </div>
      </div>

      <div className="mt-8 text-center">
        <button
          onClick={() => onViewChange('chat')}
          className="btn-primary"
        >
          Back to Chat
        </button>
      </div>
    </div>
  );
};

export default QuizInterface;