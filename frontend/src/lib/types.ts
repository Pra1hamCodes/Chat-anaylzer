export type UserStats = {
  user: string;
  messages: number;
  words: number;
  chars: number;
  media: number;
  links: number;
  emojis: number;
  unique_emojis: number;
  top_emoji: string | null;
  avg_msg_words: number;
  avg_msg_chars: number;
  first_message: string | null;
  last_message: string | null;
  active_days: number;
  pct_of_total: number;
  longest_message_chars: number;
};

export type Overview = {
  metadata: {
    total_messages: number;
    total_user_messages: number;
    total_users: number;
    total_system_events: number;
    date_range: [string, string];
    detected_format: string;
    group_name: string | null;
    parse_errors: number;
  };
  total_messages: number;
  total_user_messages: number;
  total_words: number;
  total_chars: number;
  total_media: number;
  total_links: number;
  total_emojis: number;
  unique_users: number;
  active_days: number;
  msgs_per_day: number;
  most_active_date: string | null;
  least_active_date: string | null;
  top_users: UserStats[];
};
