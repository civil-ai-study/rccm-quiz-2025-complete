#!/usr/bin/env python3
"""
🛡️ ULTRA SAFE セッション管理関数
副作用ゼロの安全なセッション操作関数群
"""

def safe_exam_session_reset():
    """
    安全なセッション初期化
    複数箇所のsession.pop呼び出しを一元化
    """
    keys_to_remove = ['exam_question_ids', 'exam_current', 'exam_category']
    removed_keys = []
    
    for key in keys_to_remove:
        if key in session:
            session.pop(key, None)
            removed_keys.append(key)
    
    session.modified = True
    
    # ログ出力（loggerが利用可能な場合のみ）
    try:
        logger.info(f"セッション安全リセット完了: {removed_keys}")
    except NameError:
        pass  # loggerが定義されていない場合は無視
    
    return len(removed_keys)

def safe_session_check():
    """
    安全なセッション状態チェック
    セッション存在確認を修正前に実行
    """
    required_keys = ['exam_question_ids', 'exam_current']
    
    # 各キーの存在と有効性をチェック
    check_result = {}
    
    for key in required_keys:
        if key in session:
            value = session[key]
            if value is not None:
                if key == 'exam_question_ids':
                    # リスト型で空でないことを確認
                    check_result[key] = isinstance(value, list) and len(value) > 0
                elif key == 'exam_current':
                    # 数値型で0以上であることを確認
                    try:
                        num_value = int(value)
                        check_result[key] = num_value >= 0
                    except (ValueError, TypeError):
                        check_result[key] = False
                else:
                    check_result[key] = True
            else:
                check_result[key] = False
        else:
            check_result[key] = False
    
    # 全てのキーが有効な場合のみTrue
    is_valid = all(check_result.values())
    
    # ログ出力（loggerが利用可能な場合のみ）
    try:
        logger.debug(f"セッション状態チェック: {check_result}, 有効: {is_valid}")
    except NameError:
        pass
    
    return is_valid

def safe_session_initialize_exam(question_ids, current_index=0, category=''):
    """
    安全なセッション初期化（試験開始用）
    エラーハンドリングを含む安全な初期化
    """
    try:
        # 入力値検証
        if not isinstance(question_ids, list) or len(question_ids) == 0:
            raise ValueError("question_idsは空でないリストである必要があります")
        
        if not isinstance(current_index, int) or current_index < 0:
            raise ValueError("current_indexは0以上の整数である必要があります")
        
        if current_index >= len(question_ids):
            raise ValueError("current_indexがquestion_idsの範囲を超えています")
        
        # セッション設定
        session['exam_question_ids'] = question_ids
        session['exam_current'] = current_index
        session['exam_category'] = category
        session.modified = True
        
        # ログ出力（loggerが利用可能な場合のみ）
        try:
            logger.info(f"セッション初期化成功: {len(question_ids)}問, カテゴリ: {category}")
        except NameError:
            pass
        
        return True
        
    except Exception as e:
        # エラーハンドリング
        try:
            logger.error(f"セッション初期化エラー: {e}")
        except NameError:
            pass
        
        # フォールバック: セッションをクリア
        safe_exam_session_reset()
        return False

def get_safe_exam_session_info():
    """
    安全なセッション情報取得
    例外処理を含む安全な情報取得
    """
    try:
        info = {
            'question_ids': session.get('exam_question_ids', []),
            'current_index': session.get('exam_current', 0),
            'category': session.get('exam_category', ''),
            'is_valid': safe_session_check(),
            'total_questions': 0,
            'progress_percent': 0
        }
        
        # 追加情報計算
        if info['question_ids']:
            info['total_questions'] = len(info['question_ids'])
            if info['total_questions'] > 0:
                info['progress_percent'] = round((info['current_index'] / info['total_questions']) * 100, 1)
        
        return info
        
    except Exception as e:
        # エラー時はデフォルト値を返す
        try:
            logger.error(f"セッション情報取得エラー: {e}")
        except NameError:
            pass
        
        return {
            'question_ids': [],
            'current_index': 0,
            'category': '',
            'is_valid': False,
            'total_questions': 0,
            'progress_percent': 0
        }

# テスト関数（開発時のみ使用）
def test_session_functions():
    """
    セッション関数のテスト
    実際のFlask環境でのみ動作
    """
    print("🧪 セッション関数テスト開始")
    
    # テスト用のモックセッション
    class MockSession(dict):
        def __init__(self):
            super().__init__()
            self.modified = False
    
    global session
    session = MockSession()
    
    # 1. 初期状態テスト
    print("1. 初期状態テスト")
    assert not safe_session_check(), "初期状態では無効である必要がある"
    print("  ✅ 初期状態チェック: 正常")
    
    # 2. セッション初期化テスト
    print("2. セッション初期化テスト")
    test_ids = [1, 2, 3, 4, 5]
    result = safe_session_initialize_exam(test_ids, 0, "テストカテゴリ")
    assert result, "初期化は成功する必要がある"
    assert safe_session_check(), "初期化後は有効である必要がある"
    print("  ✅ セッション初期化: 正常")
    
    # 3. セッション情報取得テスト
    print("3. セッション情報取得テスト")
    info = get_safe_exam_session_info()
    assert info['total_questions'] == 5, "問題数が正しい必要がある"
    assert info['is_valid'], "有効状態である必要がある"
    print("  ✅ セッション情報取得: 正常")
    
    # 4. セッションリセットテスト
    print("4. セッションリセットテスト")
    removed_count = safe_exam_session_reset()
    assert removed_count >= 0, "削除されたキー数が返される必要がある"
    assert not safe_session_check(), "リセット後は無効である必要がある"
    print("  ✅ セッションリセット: 正常")
    
    print("✅ 全テスト完了")

if __name__ == "__main__":
    # スタンドアロンテスト実行
    test_session_functions()