
import { Trophy, Lock, CheckCircle2 } from 'lucide-react';
import './Gamification.css';

const allAchievements = [
  {
    name: 'First Step',
    description: 'Complete your first activity',
    icon: '🌱'
  },
  {
    name: 'Focused Learner',
    description: 'Complete 5 activities',
    icon: '🔥'
  },
  {
    name: 'Task Master',
    description: 'Complete 10 activities',
    icon: '🏆'
  },
  {
    name: 'Project Finisher',
    description: 'Complete 2 projects',
    icon: '🚀'
  },
  {
    name: 'Exam Champion',
    description: 'Complete 2 exams',
    icon: '🎓'
  },
  {
    name: 'XP Champion',
    description: 'Earn 500 XP',
    icon: '💎'
  }
];

export default function AchievementBadges({
  badges = [],
  completed = 0,
  xp = 0
}) {
  const earnedNames = badges.map(badge => badge.name);

  return (
    <section className="panel gamification-panel achievement-panel">
      <div className="gamification-heading">
        <div>
          <span className="section-kicker">YOUR LEARNING JOURNEY</span>
          <h3><Trophy size={21} /> Your Achievements</h3>
          <p className="gamification-subtitle">
            Every completed activity brings you closer to a new achievement.
          </p>
        </div>
      </div>

      <div className="achievement-summary">
        <div>
          <strong>{earnedNames.length}/{allAchievements.length}</strong>
          <span>Badges unlocked</span>
        </div>

        <div>
          <strong>{completed}</strong>
          <span>Activities completed</span>
        </div>

        <div>
          <strong>{xp}</strong>
          <span>Total XP earned</span>
        </div>
      </div>

      <div className="achievement-grid">
        {allAchievements.map(achievement => {
          const earned = earnedNames.includes(achievement.name);

          return (
            <div
              className={`achievement-card ${
                earned ? 'achievement-earned' : 'achievement-locked'
              }`}
              key={achievement.name}
            >
              <div className="achievement-icon">
                {earned ? achievement.icon : <Lock size={23} />}
              </div>

              <div className="achievement-info">
                <h4>{achievement.name}</h4>
                <p>{achievement.description}</p>

                <small>
                  {earned ? (
                    <>
                      <CheckCircle2 size={13} />
                      Unlocked
                    </>
                  ) : (
                    'Not unlocked yet'
                  )}
                </small>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
