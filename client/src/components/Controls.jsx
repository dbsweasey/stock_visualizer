export default function Controls({ intervals, control }) {
  console.log(intervals)
  return (
    <div>
      {intervals.map(({ value, label }) => (
        <button key={value} onClick={() => control(value)}>{label}</button>
      ))}
    </div>
  );
}