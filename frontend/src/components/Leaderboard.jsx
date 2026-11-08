
import { Trophy, Medal, Crown, Zap, Award } from 'lucide-react';
import './Gamification.css';

export default function Leaderboard({
  students = [],
  myPerformance = null
}) {
  const topStudents = students.slice(0, 3);

  return (
    <section className="panel gamification-panel leaderboard-panel">
      <div className="gamification-heading">
        <div>
          <span className="section-kicker">LEARNOVA COMMUNITY</span>
          <h3><Trophy size={21} /> Student Leaderboard</h3>
          <p className="gamification-subtitle">
            Learn, complete activities and climb the rankings.
          </p>
        </div>
        <span className="leaderboard-count">
          {students.length} students
        </span>
      </div>

      {myPerformance && (
        <div className="my-rank-card">
          <div className="my-rank-icon">
            <Crown size={23} />
          </div>
          <div className="my-rank-details">
            <span>Your current position</span>
            <strong>Rank #{myPerformance.rank}</strong>
          </div>
          <div className="my-rank-xp">
            <Zap size={17} />
            <strong>{myPerformance.xp} XP</strong>
          </div>
        </div>
      )}

      {topStudents.length > 0 ? (
        <>
          <div className="top-students">
            {topStudents.map(student => (
              <div
                className={`top-student-card rank-${student.rank}`}
                key={student.user_id}
              >
                <div className="top-student-medal">
                  {student.rank === 1 ? (
                    <Crown size={25} />
                  ) : student.rank === 2 ? (
                    <Medal size={25} />
                  ) : (
                    <Award size={25} />
                  )}
                </div>

                <div className="student-avatar">
                  {student.name?.charAt(0)?.toUpperCase() || 'S'}
                </div>

                <strong>{student.name}</strong>
                <span className="student-rank-label">
                  Rank #{student.rank}
                </span>

                <div className="student-xp">
                  <Zap size={15} />
                  {student.xp} XP
                </div>

                <small>
                  {student.completed} activities completed
                </small>
              </div>
            ))}
          </div>

          <div className="leaderboard-list">
            <h4>All student rankings</h4>

            {students.map(student => (
              <div
                className={`leaderboard-row ${
                  student.user_id === myPerformance?.user_id
                    ? 'current-student'
                    : ''
                }`}
                key={student.user_id}
              >
                <span className="leaderboard-position">
                  #{student.rank}
                </span>

                <div className="leaderboard-avatar">
                  {student.name?.charAt(0)?.toUpperCase() || 'S'}
                </div>

                <div className="leaderboard-student-info">
                  <strong>{student.name}</strong>
                  <small>
                    {student.completed} activities completed
                  </small>
                </div>

                <span className="leaderboard-points">
                  <Zap size={15} />
                  {student.xp} XP
                </span>
              </div>
            ))}
          </div>
        </>
      ) : (
        <div className="gamification-empty">
          <Trophy size={34} />
          <h4>No rankings yet</h4>
          <p>Complete your first activity to start earning XP.</p>
        </div>
      )}
    </section>
  );
}
