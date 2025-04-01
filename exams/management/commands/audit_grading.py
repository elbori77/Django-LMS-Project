import json
import csv
from django.core.management.base import BaseCommand
from exams.models import Question


class Command(BaseCommand):
    help = "Audit grading logic for all question types. Logs to grading_audit_log.csv"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("🔍 Auditing grading logic...\n"))

        total = 0
        passed = 0
        failed = []

        for q in Question.objects.all():
            total += 1
            result = self.test_question(q)

            if result["pass"]:
                passed += 1
            else:
                failed.append(result)
                self.stdout.write(self.style.ERROR(f"[FAIL] {result['message']}"))

        self.stdout.write(self.style.SUCCESS(f"\n✅ Audit Complete: {passed}/{total} passed."))

        if failed:
            self.save_failures_to_csv(failed)
            self.stdout.write(self.style.WARNING("⚠️ Failures saved to grading_audit_log.csv"))

    def save_failures_to_csv(self, failed_results):
        with open("grading_audit_log.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["question_id", "type", "reason", "expected", "submitted"])
            writer.writeheader()
            for fail in failed_results:
                writer.writerow(fail["log"])

    def test_question(self, question):
        qid = question.id
        qtype = question.question_type
        correct = question.correct_option

        if qtype == "multiple_choice" or qtype == "true_false":
            selected = correct
            passed = self.grade_multiple_choice(selected, correct)
            return {
                "pass": passed,
                "message": f"{qtype.upper()} QID {qid}: {selected} vs {correct}",
                "log": {
                    "question_id": qid,
                    "type": qtype,
                    "reason": "MC/TF mismatch" if not passed else "",
                    "expected": correct,
                    "submitted": selected
                }
            }

        elif qtype == "drag_and_drop":
            try:
                pairs = question.extra_data.get("pairs", {})
                submitted = ",".join([f"{k}->{pairs[k]}" for k in pairs])
                passed = self.grade_drag_and_drop(submitted, pairs)

                return {
                    "pass": passed,
                    "message": f"DnD QID {qid}: {submitted} vs {pairs}",
                    "log": {
                        "question_id": qid,
                        "type": "drag_and_drop",
                        "reason": "DnD mismatch" if not passed else "",
                        "expected": str(pairs),
                        "submitted": submitted
                    }
                }
            except Exception as e:
                return {
                    "pass": False,
                    "message": f"DnD QID {qid}: ERROR - {str(e)}",
                    "log": {
                        "question_id": qid,
                        "type": "drag_and_drop",
                        "reason": f"Exception: {str(e)}",
                        "expected": "valid dict in extra_data['pairs']",
                        "submitted": "error"
                    }
                }

        return {
            "pass": False,
            "message": f"QID {qid}: Unknown type {qtype}",
            "log": {
                "question_id": qid,
                "type": qtype,
                "reason": "Unsupported type",
                "expected": correct,
                "submitted": "N/A"
            }
        }

    def grade_multiple_choice(self, selected, correct):
        return selected == correct

    def grade_drag_and_drop(self, submitted, correct_pairs):
        try:
            submitted_pairs = dict(pair.split("->") for pair in submitted.split(",") if "->" in pair)
            return submitted_pairs == correct_pairs
        except:
            return False
