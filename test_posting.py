from posting_system import PostingSystem

def main():
    posting_system = PostingSystem()
    # 手动触发一次发帖循环
    posting_system.run_posting_cycle()

if __name__ == "__main__":
    main()
