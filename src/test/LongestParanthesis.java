package test;

public class LongestParanthesis {
    public int longestValidParentheses(String s) {
        int count=0;
        String[] str = s.split("");
        int open=0;
        int close=0;
        for(int i=0;i<str.length;i++){
            if(str[i].equals("(")){
                open++;
            }else{
                close++;
            }
            if(open==close){
                count = Math.max(count,open+close);
            }else if(close>open){
                open=0;
                close=0;
            }
        }
        open = 0;
        close=0;
        for(int i=str.length-1;i>=0;i--){
            if(str[i].equals("(")){
                open++;
            }else{
                close++;
            }
            if(open==close){
                count = Math.max(count, open+close);
            }else if(open>close){
                open=0;
                close=0;
            }
        }
        return count;
    }

    public static void main(String[] args) {
        LongestParanthesis lp = new LongestParanthesis();
        System.out.println(lp.longestValidParentheses("(()()("));
    }
}
